# pyhiamp


<img align="right" src="neuroialogo.png" alt="Neuro-IA Lab" width="210">

**PyHIamp** (PHA) es una librería para recibir y almacenar datos (EEG, EMG, ECG y EOG) provenientes del amplifcador [g.HIamp](https://www.gtec.at/product/g-hiamp-256-channel-biosignal-amplifier/?srsltid=AfmBOopsnqXDTC9HQtDxvuPybDzjuMH8TxZDeXKLqy3aMGgrcF2gX5dc) entre otras características (ver sección [Características](#características)).

PHA utiliza [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer/?tab=readme-ov-file) (LSL) como interfaz entre g.HIamp y Python a través de [PyLSL](https://github.com/labstreaminglayer/pylsl) . LSL es un sistema para la transmisión de datos de tiempo real entre aplicaciones en la misma máquina o en la red.

PyHIamp es un desarrollo del **Laboratorio de Neruociencias e Inteligencia Artificial Aplicada** (Neuro-IA Lab) de la *Universidad Tecnológica del Uruguay*.

### Autor

- [Lucas Baldezzari](https://www.linkedin.com/in/lucasbaldezzari/)

# Funcionamiento geneal

El emplificador g.HIAMP envía los datos de la señal de EEG y los eventos registrados por el trigbox a través de g.NEEDAccess. Utilizando el protocolo LSL, los datos son transmitidos a través de la red local a una dirección IP y puerto específicos. En el lado del cliente, PyLSL recibe los datos y los almacena en un archivo XDF.

- ¿Qué rol juega [App-LabRecorder](https://github.com/labstreaminglayer/App-LabRecorder)?
- ¿Cómo envío marcadores desde LSL hacia pylsl? ¿puedo hacerlo desde pylsl hacia LSL?

# Características

- [ ] Recibir datos de EEG
- [ ] Recibir datos de EMG
- [ ] Recibir datos de ECG
- [ ] Recibir datos de EOG
- [ ] Recibir datos de eventos
- [x] Recibir datos de marcadores

# Dependencias

- g.NeedAccess (g.HIamp)
- [Lab Streaming Layer](https://github.com/labstreaminglayer) (LSL). Docs [here](https://labstreaminglayer.readthedocs.io/).
- [App-Input](https://github.com/labstreaminglayer/App-Input)
- PyLSL
- Python 3.10+
- NumPy
- SciPy
- Matplotlib
- Pandas
- PyQt5

# Instalación

# Ejemplos de uso

# Documentación

# Licencia

# Referencias

- [Lab Streaming Layers for Brain Data with Python](https://www.youtube.com/watch?v=oLulfdNI3E0&ab_channel=EsbenKran)
- [Demo 1 The Lab Streaming Layer](https://www.youtube.com/watch?v=Y1at7yrcFW0&ab_channel=TheQualcommInstitute)