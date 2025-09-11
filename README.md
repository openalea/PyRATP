# PyRATP
[![Docs](https://readthedocs.org/projects/pyratp/badge/?version=latest)](https://pyratp.readthedocs.io/)
[![Build Status](https://github.com/openalea/PyRatp/actions/workflows/conda-package-build.yml/badge.svg?branch=master)](https://github.com/openalea/PyRatp/actions/workflows/conda-package-build.yml?query=branch%3Amaster)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License--CeCILL-C-blue)](https://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html)
[![Anaconda-Server Badge](https://anaconda.org/openalea3/pyratp/badges/version.svg)](https://anaconda.org/openalea3/pyratp)

## Software

### Authors
> -   Herve Sinoquet
> -   Marc Saudreau
> -   Jerome Ngao
> -   Boris Adam
> -   Christophe Pradal
> -   Christian Fournier 
> -   Fabrice Bauget

### Description
RATP: Radiation Absorption, Transpiration and Photosynthesis

### Status
Python package

### License
CecILL-C
**URL** : <https://hydroroot.rtfd.io>

### Dependencies
- meson-python
- numpy
- pandas
- scipy
- openalea.plantgl
- openalea.mtg
- QtPy

### Modifications 
- Installation with make: it compiles fortran part with f2py then installs the package with setuptools and pip
- Compute transmitted radiation for each voxel
- Intercepted and transmitted radiation among the output results
- leaf angle distribution for each voxel
- Local or solar hour option for computing sun position
- Possibility for external use of the sun computation routine

## Installation 
### for user
1) Install Miniforge: [https://github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge)
2) Create a conda environment:
```shell
mamba create -n pyratp openalea.ratp -c conda-forge -c openalea3
```
3) activate the environment: `mamba activate pyratp`

The user has the possibility to install the package from a candicate release channel 
of the conda repository of openalea as follows:
```shell
mamba create -n pyratp openalea.ratp -c conda-forge -c openalea3/label/rc
```
The rc channel corresponds to the latest build of PyRatp when the main channel is the 
stable release.

### For developpers
Editable install with conda/environment.yml is not functionning because of namespace conflict. A workaround is as follow:
1) download the repository and change to the root directory:
```shell
   git clone https://github.com/openalea/PyRATP.git
   cd PyRATP
```
2) Create a conda environment with dependencies manually with:
```shell
mamba create -n pyratp -c conda-forge -c openalea3 openalea.plantgl openalea.mtg qtpy compilers meson-python
```
3) activate the environment: `mamba activate pyratp`

4) Build the fortran library:
```shell
meson setup builddir
meson compile -C builddir
cp builddir/src/openalea/ratp/pyratp.cpython-312-x86_64-linux-gnu.so src/openalea/ratp
```
5) modify the Python path:
via the environment variable

```shell
export PYTHONPATH="$HOME/mypathPyRatp/src"
```

or

add the path to `src` in your ipython or in IDE with:
```ipython
import sys; sys.path.extend([mypath to 'src'])
```
with `mypath to 'src'` the absolute path to 'PyRatp/src'
