from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from pyhiamp.markers.MarkersGenerator import MarkersGenerator
from pyhiamp.gui.SquareWidget import SquareWidget
from pyhiamp.utils.decorators import TimerLogger, intervalCounter
import logging
import sys
import numpy as np

logging.basicConfig(level=logging.WARNING)  # Configuración básica del logger

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

marcador_inicio = SquareWidget(x=200, y=200, size=120, color="black",
                         text="Inicio Sesión", text_color="white")
marcador_cue = SquareWidget(x=400, y=200, size=120, color="black",
                         text="Cue", text_color="white")
marcador_precue = SquareWidget(x=600, y=200, size=120, color="black",
                         text="Precue", text_color="white")
marcador_calibration = SquareWidget(x=800, y=200, size=120, color="white",
                         text="Para calibrar\n sensores", text_color="black")

phases = {
    "start": {"next": "rest", "duration": 5.0},
    "rest": {"next": "precue", "duration": 2.0},
    "precue": {"next": "cue", "duration": 0.5},
    "cue": {"next": "evaluate", "duration": 3.0},
    "evaluate": {"next": "rest", "duration": 2.0},
    "first_jump": {"next": "start", "duration": 0.1},}
markerGen = MarkersGenerator(phases, stream_name="Test_Markers", stream_type="Markers")

logger = TimerLogger()

@intervalCounter(logger)
def update_markers():
    if markerGen.update():
        logging.debug(f"Marcador enviado: {markerGen.in_phase}")
        if markerGen.in_phase == "start":
            marcador_inicio.change_color("#ffffff")
            marcador_cue.change_color("#000000")
            marcador_precue.change_color("#000000")
            ##dejo sin texto
            marcador_inicio.change_text("")
            marcador_cue.change_text("")
            marcador_precue.change_text("")
        elif markerGen.in_phase == "precue":
            marcador_inicio.change_color("#000000")
            marcador_precue.change_color("#ffffff")
            marcador_cue.change_color("#000000")
        elif markerGen.in_phase == "cue":
            marcador_precue.change_color("#000000")
            marcador_inicio.change_color("#000000")
            marcador_cue.change_color("#ffffff")
        elif markerGen.in_phase == "evaluate":
            marcador_cue.change_color("#000000")
            marcador_precue.change_color("#000000")

def stop_test():
    if len(logger.timestamps) > 1:
        intervals = np.diff(logger.timestamps) * 1000  # convert to ms
        print(f"\n--- Datos del timer ---")
        print(f"Muestras: {len(intervals)}")
        print(f"Media del intervalo: {np.mean(intervals):.3f} ms")
        print(f"Mediana: {np.median(intervals):.3f} ms")
        print(f"Std: {np.std(intervals):.3f} ms")
        print(f"Min: {np.min(intervals):.3f} ms")
        print(f"Max: {np.max(intervals):.3f} ms")
    app.quit()

class MainWindow(QWidget):
    def __init__(self, funcs_to_run, times_for_funcs):
        super().__init__()
        self.setWindowTitle("Presione Enter para iniciar o Escape para salir")
        self.setGeometry(100, 100, 400, 300)
        #agrego un texto central en la ventana que diga Presione Enter para iniciar o Escape para salir
        self.setStyleSheet("background-color: white;")

        ##agrego los 
        self.initUI()

        ##chqueo que funcs_to_run y times_for_funcs no sean None
        if funcs_to_run is None or times_for_funcs is None:
            raise ValueError("funcs_to_run y times_for_funcs no pueden ser None")
        ##chequeo que tengan la misma longitud
        if len(funcs_to_run) != len(times_for_funcs):
            raise ValueError("funcs_to_run y times_for_funcs deben tener la misma longitud")
        
        ##genero una lista de QTimer para cada función
        self.funcs_to_run = funcs_to_run
        self.times_for_funcs = times_for_funcs
        self.timers = []
        ##agrego un timer para cada función
        for func, time in zip(funcs_to_run, times_for_funcs):
            timer = QTimer(self)
            timer.timeout.connect(func)
            timer.setInterval(time)
            self.timers.append(timer)

    def initUI(self):
        # Creamos el layout vertical
        layout = QVBoxLayout()
        
        # Creamos el label con el mismo texto del título
        label = QLabel("Presione Enter para iniciar o Escape para salir")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: black;")

        # Agregamos el label al layout
        layout.addWidget(label)

        # Asignamos el layout a la ventana
        self.setLayout(layout)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            print("Iniciando...")
            self.start_test()
        ##si se presiona Escape, se detiene el test
        elif event.key() == Qt.Key_Escape:
            print("Deteniendo...")
            self.stop()
            app.quit()

    def start_test(self):
        for timer in self.timers:
            timer.start()

    def stop(self):
        for timer in self.timers:
            timer.stop()
        ##cierro la ventana
        self.close()


# Creamos la ventana principal

window = MainWindow(funcs_to_run=[update_markers],
                    times_for_funcs=[5]) 

exit_code = app.exec_()
sys.exit(exit_code)