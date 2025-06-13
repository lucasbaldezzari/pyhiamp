from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt
from pyhiamp.markers.MarkersGenerator import MarkersGenerator
from pyhiamp.gui.SquareWidget import SquareWidget
from pyhiamp.utils.decorators import TimerLogger, intervalCounter
import logging
import sys
import numpy as np

logging.basicConfig(level=logging.WARNING)  # Configuración básica del logger

phases = {
    "precue": {"next": "cue", "duration": 4.0},
    "go": {"next": "go", "duration": 0.5},
    "cue": {"next": "evaluate", "duration": 4.0},
    "evaluate": {"next": "precue", "duration": 1.},
}

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

marcador1 = SquareWidget(x=200, y=200, size=120, color="black",
                         text="Inicio Sesión", text_color="white")
marcador2 = SquareWidget(x=400, y=200, size=120, color="black",
                         text="Run", text_color="white")

markerGen = MarkersGenerator(phases, stream_name="Test_Markers", stream_type="Markers")

logger = TimerLogger()


@intervalCounter(logger)
def update_markers():
    if markerGen.update():
        logging.debug(f"Marcador enviado: {markerGen.in_phase}")
        if markerGen.in_phase == "precue":
            marcador1.change_color("#ffffff")
            marcador2.change_color("#000000")
        else:
            marcador1.change_color("#000000")
            marcador2.change_color("#ffffff")

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
                    times_for_funcs=[1]) 

exit_code = app.exec_()
sys.exit(exit_code)