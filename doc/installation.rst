============
Installation
============

First install miniforge following the instructions given here https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html

User installation
-----------------

ratp may by installed simply on a conda environments:

::

    mamba create -n ratp -c conda-forge -c openalea3 openalea.ratp
    mamba activate ratp

That creates a conda environment called *ratp*, install in it *openalea.ratp* with all the dependencies and
activate the environment. Then just open an Ipython session and enjoy.

If you want notebook support, run for example:

::

    mamba install jupyterlab


Developpers installation (python and fortran modifications)
-----------------------------------------------------------

Editable installation with conda/environment.yml is not functioning because of namespace conflict. A workaround is as follows:
1) download the repository and change to the root directory:

::

    git clone https://github.com/openalea/PyRATP.git
    cd PyRATP

2) Create a conda environment with dependencies manually:

Using MAC and Linux:

::

    mamba create -n pyratp_dev -c conda-forge -c openalea3 openalea.plantgl openalea.mtg qtpy compilers meson-python scipy pytest jupyter

Using Windows:

::

    mamba create -n pyratp_dev -c conda-forge -c openalea3 openalea.plantgl openalea.mtg qtpy m2w64-toolchain meson-python scipy pytest gfortran jupyter

4) activate the environment: `mamba activate pyratp_dev`

5) Compile everything:

::

    pip install ."[test]"


and after each modification of the python or Fortran part, run

::

    pip install .

then restart your kernel (when using IPython) for your modifications to be taken into account.