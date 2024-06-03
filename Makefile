ifeq ($(OS), Windows_NT) 
    detected_OS := Windows
else
    detected_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
endif

BUILDFOLDER := building

ifeq ($(detected_OS), Windows)
EXTTARGET := .pyd
OPTCOMPILE := --compiler=mingw32 --fcompiler=gnu95 -DNPY_OS_MINGW 
MOVECMD := move /Y
MKDIRBUILD := if not exist $(BUILDFOLDER) mkdir $(BUILDFOLDER)
RMFILE := del
RMFOLDER := rmdir /s /q
else
EXTTARGET := .so
OPTCOMPILE := --fcompiler=gnu95
MOVECMD := mv
MKDIRBUILD := mkdir -p $(BUILDFOLDER)
RMFILE := rm
RMFOLDER := rm -r
endif

# install ou develop
mode ?= install
ifeq ($(mode), develop) 
    INSTALLOPT := --editable
else
    INSTALLOPT :=  
endif

FORTRANFILES := src/f90/mod_Cocnstant_ValuesF2PY.f90  \
				src/f90/mod_Grid3DF2PY_64bit.f90      \
				src/f90/mod_SkyvaultF2PY.f90          \
				src/f90/mod_Vegetation_TypesF2PY.f90  \
				src/f90/mod_Dir_InterceptionF2PY.f90  \
				src/f90/mod_Hemi_InterceptionF2PY.f90 \
				src/f90/mod_MicrometeoF2PY.f90        \
				src/f90/mod_Shortwave_BalanceF2PY.f90 \
				src/f90/mod_Energy_BalanceF2PY.f90    \
				src/f90/mod_PhotosynthesisF2PY.f90    \
				src/f90/mod_MinerPhenoF2PY.f90        \
				src/f90/prog_RATP.f90


# package installation in the current Python interpreter
install : src/alinea/pyratp/pyratp.pyd
	pip install $(INSTALLOPT) .

# copie within the python sources and simplify library's name
src/alinea/pyratp/pyratp.pyd: pyratp.pyd
	$(MOVECMD) pyratp.*$(EXTTARGET) src/alinea/pyratp/pyratp$(EXTTARGET)

# library compilation
pyratp.pyd: pyratp.pyf
	$(MKDIRBUILD)
	f2py -c  pyratp.pyf $(FORTRANFILES) --build-dir $(BUILDFOLDER) $(OPTCOMPILE)

# creation of the header
pyratp.pyf: 
	python -m numpy.f2py -m pyratp -h $@ $(FORTRANFILES) --lower

clean:
	$(RMFILE) pyratp.pyf
	$(RMFOLDER) $(BUILDFOLDER)
