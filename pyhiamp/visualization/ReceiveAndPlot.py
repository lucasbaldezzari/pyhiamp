"""
Clase basada en el ejemplo de ReceiveAndPlot.py de pylsl (ver sitio oficial)
"""

import math
from typing import List

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import pylsl

# Parámetros básicos para la ventana de graficado
plot_duration = 15  # cuántos segundos de datos mostrar
update_interval = 10  # ms entre actualizaciones de pantalla
pull_interval = 500  # ms entre cada operación de extracción de datos


class Inlet:
    """Clase base para representar una entrada que puede graficarse"""

    def __init__(self, info: pylsl.StreamInfo):
        # crear una entrada y conectarla a la salida encontrada previamente.
        # max_buflen se establece para que los datos más antiguos que plot_duration
        # se descarten automáticamente y solo extrayamos datos recientes para mostrar

        # Además, realizamos sincronización de reloj en línea para que todos los flujos
        # estén en el mismo dominio temporal que lsl_clock() local
        # (ver https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/enums.html#_CPPv414proc_clocksync)
        # y eliminar jitter de las marcas de tiempo
        self.inlet = pylsl.StreamInlet(
            info,max_buflen=plot_duration,
            processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter,)
        
        # almacenamos el nombre y la cantidad de canales
        self.name = info.name()
        self.channel_count = info.channel_count()

    def pull_and_plot(self, plot_time: float, plt: pg.PlotItem):
        """Extraer datos de la entrada y agregarlos al gráfico.
        :param plot_time: marca de tiempo mínima aún visible en el gráfico
        :param plt: el gráfico en el cual mostrar los datos
        """
        # No sabemos qué hacer con una entrada genérica, por lo que la omitimos.
        pass


class DataInlet(Inlet):
    """Una DataInlet representa una entrada con datos continuos multicanal
    que se deben graficar como múltiples líneas."""

    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo, plt: pg.PlotItem,
                 background_color=(255,255,255), lines_color='k'):
        super().__init__(info)
        # calcular el tamaño del buffer, es decir, dos veces la cantidad de datos visualizados
        bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration), info.channel_count(),)
        self.buffer = np.empty(bufsize, dtype=self.dtypes[info.channel_format()])
        empty = np.array([])
        # crear un objeto de curva por cada canal/línea que se encargará de mostrar los datos
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True, pen=pg.mkPen(color=lines_color))
               for _ in range(self.channel_count)]
        
        for curve in self.curves:
            plt.addItem(curve)

        # Setear el color de fondo del plot
        plt.getViewBox().setBackgroundColor(background_color)

    def pull_and_plot(self, plot_time, plt):
        # extraer los datos
        _, ts = self.inlet.pull_chunk(
            timeout=0.0, max_samples=self.buffer.shape[0], dest_obj=self.buffer
        )
        # ts estará vacío si no se extrajeron muestras, o contendrá una lista de timestamps en caso contrario
        if ts:
            ts = np.asarray(ts)
            y = self.buffer[0 : ts.size, :]
            this_x = None
            old_offset = 0
            new_offset = 0
            for ch_ix in range(self.channel_count):
                # no extraemos una pantalla completa de datos, así que debemos
                # recortar los datos antiguos y agregar los nuevos
                old_x, old_y = self.curves[ch_ix].getData()
                # los timestamps son idénticos para todos los canales, por lo que calculamos esto solo una vez
                if ch_ix == 0:
                    # buscar el índice de la primera muestra que aún es visible,
                    # es decir, más reciente que el borde izquierdo del gráfico
                    old_offset = old_x.searchsorted(plot_time)
                    # lo mismo para los nuevos datos, en caso de haber extraído más de lo que puede mostrarse
                    new_offset = ts.searchsorted(plot_time)
                    # agregar nuevos timestamps a los antiguos recortados
                    this_x = np.hstack((old_x[old_offset:], ts[new_offset:]))
                # agregar nuevos datos a los datos antiguos recortados
                this_y = np.hstack((old_y[old_offset:], y[new_offset:, ch_ix] - ch_ix))
                # reemplazar los datos antiguos
                self.curves[ch_ix].setData(this_x, this_y)


class MarkerInlet(Inlet):
    """Muestra eventos esporádicos como líneas verticales con colores únicos por marcador."""

    def __init__(self, info: pylsl.StreamInfo):
        super().__init__(info)
        self.marker_colors = {}  # Diccionario para asignar colores por marcador
        self.color_index = 0     # Contador de colores únicos
        self.text_items = []     # Guardamos los textos si después quisiéramos actualizarlos
        self.YTOP = 5.0          # Altura fija para mostrar los labels (ajustar según tus señales)

    def pull_and_plot(self, plot_time, plt):
        strings, timestamps = self.inlet.pull_chunk(0)
        if timestamps:
            for string, ts in zip(strings, timestamps):
                label = string[0]

                # Asignación de color por marcador
                if label not in self.marker_colors:
                    color = pg.intColor(self.color_index, hues=20)
                    self.marker_colors[label] = color
                    self.color_index += 1
                else:
                    color = self.marker_colors[label]

                # Dibujar la línea vertical
                plt.addItem(
                    pg.InfiniteLine(pos=ts, angle=90, pen=pg.mkPen(color=color, width=2), movable=False)
                )

                # Dibujar el texto encima de todo
                text = pg.TextItem(text=label, color='k', anchor=(0.5, 0), fill=pg.mkBrush('w'))
                text.setFont(QtGui.QFont("Arial", 14))
                plt.addItem(text)
                ymin, ymax = plt.viewRange()[1]
                centerY = (ymin + ymax) / 2
                text.setPos(ts, centerY)

                self.text_items.append(text)

def main():
    # primero resolvemos todos los flujos que podrían mostrarse
    inlets: List[Inlet] = []
    print("buscando flujos")
    streams = pylsl.resolve_streams()

    pg.setConfigOption('background', 'w')  
    pg.setConfigOption('foreground', 'k') 

    # Crear la ventana de pyqtgraph
    pw = pg.plot(title="LSL Plot")
    plt = pw.getPlotItem()
    plt.enableAutoRange(x=False, y=True)

    # iterar sobre los flujos encontrados, creando objetos de entrada especializados
    # que manejarán el graficado de los datos
    for info in streams:
        if info.type() == "Markers":
            if (
                info.nominal_srate() != pylsl.IRREGULAR_RATE
                or info.channel_format() != pylsl.cf_string
            ):
                print("Flujo de marcadores inválido " + info.name())
            print("Agregando entrada de marcador: " + info.name())
            inlets.append(MarkerInlet(info))
        elif (
            info.nominal_srate() != pylsl.IRREGULAR_RATE
            and info.channel_format() != pylsl.cf_string
        ):
            print("Agregando entrada de datos: " + info.name())
            inlets.append(DataInlet(info, plt, background_color=(255,255,255), lines_color='k'))
        else:
            print("No sé qué hacer con el flujo " + info.name())

    def scroll():
        """Mover la vista para que los datos parezcan desplazarse"""
        # Mostramos los datos hasta un instante justo antes del tiempo actual
        # para que los nuevos datos no aparezcan de repente en el centro del gráfico
        fudge_factor = pull_interval * 0.002
        plot_time = pylsl.local_clock()
        pw.setXRange(plot_time - plot_duration + fudge_factor, plot_time - fudge_factor)

    def update():
        # Leer datos de la entrada. Usamos un timeout de 0.0 para no bloquear la GUI.
        mintime = pylsl.local_clock() - plot_duration
        # llamar a pull_and_plot para cada entrada.
        # El manejo específico de tipos de entrada (marcadores, datos continuos) se realiza
        # en las diferentes clases de entrada.
        for inlet in inlets:
            inlet.pull_and_plot(mintime, plt)

    # crear un temporizador que moverá la vista cada update_interval ms
    update_timer = QtCore.QTimer()
    update_timer.timeout.connect(scroll)
    update_timer.start(update_interval)

    # crear un temporizador que extraerá y agregará nuevos datos ocasionalmente
    pull_timer = QtCore.QTimer()
    pull_timer.timeout.connect(update)
    pull_timer.start(pull_interval)

    import sys

    # Iniciar el bucle de eventos de Qt a menos que estemos en modo interactivo o usando pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        QtGui.QGuiApplication.instance().exec()


if __name__ == "__main__":
    main()