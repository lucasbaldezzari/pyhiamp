import random
import time
import numpy as np
import keyboard
from pylsl import StreamInfo, StreamOutlet, local_clock
import logging

logging.basicConfig(level=logging.WARNING)# Configuración básica del logger

def safe_lsl_send(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logging.error(f"[Error enviando marcador LSL]: {e}")
    return wrapper

class MarkersGenerator:
    def __init__(self, phases: dict, stream_name="MarkersGenerator", stream_type="Markers", sourceID=None):
        self.phases = phases
        self.stream_name = stream_name
        self.stream_type = stream_type
        self.in_phase = list(phases.keys())[-1]
        self.next_transition = -1

        self.creation_time = local_clock()
        self.accumulated_time = 0.0
        self._last_phase_time = self.creation_time

        if sourceID is None:
            sourceID = f"MarkersGenerator_{random.randint(1000, 9999)}"

        self.outlet_info = StreamInfo(
            name=stream_name,
            type=stream_type,
            nominal_srate=0,
            channel_format="string",
            channel_count=1,
            source_id=sourceID)
        self.outlet = StreamOutlet(self.outlet_info)
        logging.info(f"Creando un outlet con nombre {stream_name} y tipo {stream_type}")

    def _makeMensaje(self, mensaje):
        return f"{self.in_phase}_{mensaje}" if mensaje else self.in_phase

    def _advance_phase(self, mensaje=""):
        """
        Función para avanzar a la siguiente fase y enviar un marcador.
        """
        now = local_clock()
        self.accumulated_time += now - self._last_phase_time
        self._last_phase_time = now

        self.in_phase = self.phases[self.in_phase]["next"]
        self.next_transition = now + self.phases[self.in_phase]["duration"]
        self.outlet.push_sample([self._makeMensaje(mensaje)])

    @safe_lsl_send
    def next(self, mensaje=""):
        """
        Método para enviar el siguiente marcador dentro de MarkersGenerator.phases
        Usar este método si se necesita enviar marcadores de manera asíncrona.
        """
        self._advance_phase(mensaje)

    @safe_lsl_send
    def update(self, mensaje=""):
        """
        Método para enviar un marcador de manera automática en base los tiempos
        "duration" dentro de MarkersGenerator.phases.

        Con este método nos aseguramos de enviar un marcador solamente cuando
        se superen los tiempos de cada fase.

        Usar este método cuando se desee cierta temporalidad en el envío de marcadores.
        """
        now = local_clock()
        if now > self.next_transition:
            self._advance_phase(mensaje)
            return True
        return False
    
    def moveTo(self, phase_name, mensaje=""):
        """
        Método para mover manualmente a una fase específica y enviar un marcador.
        """
        if phase_name in self.phases:
            self.in_phase = phase_name
            self.next_transition = local_clock() + self.phases[phase_name]["duration"]
            self._last_phase_time = local_clock()
            self.outlet.push_sample([self._makeMensaje(mensaje)])
        else:
            logging.error(f"Fase '{phase_name}' no encontrada en las fases definidas.")

    def get_elapsed_time(self):
        return local_clock() - self.creation_time

    def get_accumulated_time(self):
        return self.accumulated_time
    
if __name__ == "__main__":
    phases = {"precue": {"next": "cue", "duration": 1.0},
              "cue": {"next": "go", "duration": 0.5},
              "go": {"next": "evaluate", "duration": 2.0},
              "evaluate": {"next": "precue", "duration": 0.5},}
    
    markerGen = MarkersGenerator(phases,stream_name="Test_Markers",stream_type="Markers")
    markerGen.next()
    try:
        while True:
            if markerGen.update():
                logging.debug(f"Marcador enviado: {markerGen.in_phase}")
                logging.debug(f"Tiempo acumulado: {markerGen.get_accumulated_time()}")
            if keyboard.is_pressed("esc"):
                logging.info("Escape por usuario. Saliendo...")
                break

    except KeyboardInterrupt:
        logging.info("Nos fuimos...")
        pass