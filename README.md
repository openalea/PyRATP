# PyRATP
RATP: Radiation Absorption, Transpiration and Photosynthesis

## Dependencies
- meson-python
- numpy > 1.22
- pandas
- scipy
- openalea.plantgl
- openalea.mtg
- QtPy

## Modifications 
- Installation with make: it compiles fortran part with f2py then installs the package with setuptools and pip
- Compute transmitted radiation for each voxel
- Intercepted and transmitted radiation among the output results
- leaf angle distribution for each voxel
- Local or solar hour option for computing sun position
- Possibility for external use of the sun computation routine

## Installation 
### with conda
1) install miniconda 64 bits: https://docs.conda.io/en/latest/miniconda.html
2) Create a conda environment:
```shell
conda create -n pyratp PyRatp -c conda-forge -c openalea3
```
3) set conda in the created environment: `conda activate pyratp`

### with pip for developer
1) Create a conda environment:
```shell
conda create -n pyratp openalea.mtg openalea.plantgl QtPy -c conda-forge -c openalea3
conda activate pyratp
```
2) download the repository and change to the root directory:
```shell
   git clone https://github.com/openalea/PyRATP.git
   cd PyRATP
```
3) install the package with pip in dev mode:
```shell
    pip install -e .
```
4) test the package:
- install pytest `mamba install pytest`
- run test
```shell
    cd test
    pytest -v --ignore=test_complet.py
```
