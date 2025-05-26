# pyhiamp

<img align="right" src="neuroialogo.png" alt="Neuro-IA Lab" width="210">

**PyHIamp** (PHA) es una librería para recibir y almacenar datos (EEG, EMG, ECG y EOG) provenientes del amplifcador [g.HIamp](https://www.gtec.at/product/g-hiamp-256-channel-biosignal-amplifier/?srsltid=AfmBOopsnqXDTC9HQtDxvuPybDzjuMH8TxZDeXKLqy3aMGgrcF2gX5dc) entre otras características (ver sección [Características](#características)).

PHA utiliza [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer/?tab=readme-ov-file) (LSL) como interfaz entre g.HIamp y Python a través de [PyLSL](https://github.com/labstreaminglayer/pylsl) . LSL es un sistema para la transmisión de datos de tiempo real entre aplicaciones en la misma máquina o en la red.

PyHIamp es un desarrollo del **Laboratorio de Neruociencias e Inteligencia Artificial Aplicada** (Neuro-IA Lab) de la *Universidad Tecnológica del Uruguay*.

## Autor

- [Lucas Baldezzari](https://www.linkedin.com/in/lucasbaldezzari/)

## Versión

- 0.1.1: Se implementa método streaming.signal._getSyntheticEEG() para generar eeg sintéticos. Se mejorará a un espectro 1/f.

## Funcionamiento geneal

El emplificador g.HIAMP envía los datos de la señal de EEG y los eventos registrados por el trigbox a través de g.NEEDAccess. Utilizando el protocolo LSL, los datos son transmitidos a través de la red local con una IP y puerto específicos. Por otro lado, usando PyLSL se generan eventos y marcadores importantes de la sesión expermiental. Además, se pueden recibir datos para graficarlos en tiempo real.

Los datos provenientes del amplificador, como los eventos y marcadores generados con PyLSL se guardan en un archivo XDF a través de [LabRecorder](https://github.com/labstreaminglayer/App-LabRecorder)

## Características

- [ ] Recibir datos de señal y eventos provenientes de g.HIamp y almacenarlos en un archivo XDF usando LabRecorder.
- [ ] Generar eventos y enviarlos a través de LSL.
- [X] Almacenar los datos en un archivo [XDF](https://github.com/sccn/xdf) usando LabRecorder.
- [ ] Entorno gráfico para ejecutar los módulos de PyHiamp de manera separada, con mensajes de estado de sesión, entre otros datos útiles.
- [X] Sintetizador de señal para emular el g.HIAMP.

## Dependencias

- [liblsl](https://github.com/sccn/liblsl/releases)
- [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer/) (LSL). Documentación oficial [acá](https://labstreaminglayer.readthedocs.io/).
- [App-Input](https://github.com/labstreaminglayer/App-Input)
- g.NeedAccess (g.HIamp)
- Python 3.12
- [PyLSL](https://github.com/labstreaminglayer/pylsl)
- [pyxdf](https://github.com/xdf-modules/pyxdf/tree/main) para lectura de archivos XDF. El formato de los XDF puede estudiarse [acá](https://github.com/sccn/xdf/wiki/Specifications). La meta data recomendada para archivos que contengan información de EEG se puede encontrar [acá](https://github.com/sccn/xdf/wiki/EEG-Meta-Data).
- NumPy
- SciPy
- Matplotlib
- Pandas
- PyQt6

## Instalación

### 1. Creando un entorno virtual

Se recomienda crear un entorno virtual para instalar las dependencias de python y los archivos de *liblsl*. Para crear un entorno virtual se puede usar el comando ``conda create --name <nombre_entorno> python=3.12`` (asumiendo que se tiene instalado [miniconda](https://www.anaconda.com/download)).

### 2. Descargando liblsl

El primer paso es descargar la librería [liblsl](https://github.com/sccn/liblsl). Hay dos formas de obtener la librería:

1. Desde la [Release page](https://github.com/sccn/liblsl/releases).
2. Desde la [nube de Anaconda](https://anaconda.org/conda-forge/liblsl) ejecutando ``conda install -c conda-forge liblsl`` (forma recomendada habiendo activado el entorno virtual del paso [1](https://github.com/lucasbaldezzari/pyhiamp?tab=readme-ov-file#1-creando-un-entorno-virtual)).

Más info [Getting and using liblsl](https://github.com/sccn/liblsl?tab=readme-ov-file#getting-and-using-liblsl).

### 3. Instalando PyLSL

Para instalar PyLSL se puede usar el comando ``pip install pysls`` (es importante haber activado el entorno virtual del paso [1](https://github.com/lucasbaldezzari/pyhiamp?tab=readme-ov-file#1-creando-un-entorno-virtual)).

### 4. Instalando PyHIamp

Para instalar PyHIamp se puede usar el comando ``pip install pyhiamp`` (es importante haber activado el entorno virtual del paso [1](https://github.com/lucasbaldezzari/pyhiamp?tab=readme-ov-file#1-creando-un-entorno-virtual)).

### 5. Instalando LabRecorder

Descargar e instalar [LabRecorder](https://github.com/labstreaminglayer/App-LabRecorder).

### 6. Obteniendo datos desde g.HIAMP

Para poder obtener datos desde el almplificador g.HIAMP es necesario ejectutar gNEEDaccess de LSL. Se puede descargar desde aquí [App-g.Tec/gNEEDaccess](https://github.com/labstreaminglayer/App-g.Tec/releases) o bien se puede descargar la versión *v0.14* desde la sección [apps](https://github.com/lucasbaldezzari/pyhiamp/tree/main/apps).

#### Importante

- Para que gNEEDaccess funcione correctamente es necesario que el servicio GDSServerService esté ejecutandose. En las pruebas realizadas, este servicio se ejecuta cuando se inicia *g.TecSuite*.
- En mi experiencia, para poder obtener datos desde el g.HIAMP es necesario,
1. Escanear el amplifcador con *Scan*.
2. Conectar con *Connect*.
3. Configurar el dispositivo con *Config Device*, aún si no hay nada que configurar, es necesario entrar a la ventana.
4. Iniciar streaming con *Start*.

### 7. Uso

En teoría, todo está listo para usar PyHIamp.

## Instaladores y ropositorios de paquetes

## Ejemplos de uso

## Documentación

## Referencias

- [Lab Streaming Layers for Brain Data with Python](https://www.youtube.com/watch?v=oLulfdNI3E0&ab_channel=EsbenKran)
- [Demo 1 The Lab Streaming Layer](https://www.youtube.com/watch?v=Y1at7yrcFW0&ab_channel=TheQualcommInstitute)
- [liblsl docs](https://labstreaminglayer.readthedocs.io/projects/liblsl/index.html)