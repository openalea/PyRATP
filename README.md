# PyRATP (MobiDiv)
Fork from alinea.pyratp: https://github.com/openalea-incubator/PyRATP

RATP: Radiation Absorption, Transpiration and Photosynthesis

## Dependencies
- make
- gcc 64 bits 
- Python 3
- numpy
- pandas
- scipy
- openalea.plantgl
- openalea.mtg

## Modifications 
- Installation with make: it compiles fortran part with f2py then installs the package with setuptools and pip
- Compute transmitted radiation for each voxel
- Intercepted and transmitted radiation among the output results
- leaf angle distribution for each voxel
- Local or solar hour option for computing sun position
- Possibility for external use of the sun computation routine

## Installation example with conda
1) install gcc 64 bits (MinGW with Windows OS)
2) install miniconda 64 bits: https://docs.conda.io/en/latest/miniconda.html
3) Create a conda environment:
```shell
conda create -n myenvname openalea.mtg openalea.plantgl numpy=1.20.3 scipy pandas -c conda-forge -c fredboudon
```
4) set conda in the created environment: `conda activate myenvname`
5) download the repository: 
   1) `git clone git@github.com:mwoussen/PyRATP_MobiDiv.git` or `git clone https://github.com/mwoussen/PyRATP_MobiDiv.git`
   2) `cd PyRATP_MobiDiv`
6) install the package: `make`
    if you want to edit the source files in the current folder : `make mode=develop`
7) clean the compilation step: `make clean`
8) test the package: `python tests/smalltests.py`

## Troubleshootings
### Installation under Windows OS
- PyRATP_Mobidiv works only in 64 bits
- It seems like the installation doesn't work with numpy >= 1.23
- Compilation error: `undefined reference to __intrinsic_setjmpex l.3335 pyratpmodule.c` 
    1) replace `#include<setjmp.h>` with `#include<setjmpex.h>` in the file `pyratpmodule.c` (building folder)
    2) relauch the compilation `f2py -c ...` l.58 in the Makefile 
