from setuptools import setup, find_packages

setup(
    name="pyhiamp",
    version="0.1.0",
    author="Lucas BALDEZZARI",
    author_email="lucas.baldezzari@utec.edu.uy",
    description="Paquete para obtener datos desde el g.HIAMP de g.tec usando LSL",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "mne",
        "scikit-learn",
        "pylsl",
        "pyqtgraph",
        "pandas",
        "keyboard"
    ],
    python_requires=">=3.10",
)