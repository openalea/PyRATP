**RATP version 2 in OpenAlea environment**

**User’s Guide**

**H. Sinoquet, UMR PIAF, Clermont-Ferrand, France**

**INTRODUCTION**

The model **RATP** (Radiation Absorption, Transpiration and
Photosynthesis) was designed to simulate the spatial distribution of
radiation and leaf-gas exchanges within vegetation canopies as a
function of canopy structure, canopy microclimate within the canopy and
physical and physiological leaf properties. The model uses a 3D
representation of the canopy (i.e. an array of 3D voxels, each
characterised by a leaf area density) and allows several vegetation
types (e.g. foliage of several plants) to be input at voxel scale.
Radiation transfer is computed by a turbid medium analogy, transpiration
by the leaf energy budget approach, and photosynthesis by the Farquhar
model, each applied for sunlit and shaded leaves at the individual 3D
cell-scale. The model typically operates at a 20 to 30 min time step.
Principes and main equations of the RATP model are given in: Sinoquet H,
Le Roux X, Adam B, Améglio T, Daudet FA, 2001. RATP, a model for
simulating the spatial distribution of radiation absorption,
transpiration and photosynthesis within canopies: application to an
isolated tree crown. Plant Cell and Environment, 24, 395-406.

The RATP version 2 is basically implemented as a set of Fortran90
modules, which can be used as a Python library in the OpenAlea
environment. A Fortran90 module includes public variables and
subroutines, which are all accessible in the OpenAlea environment.

**SOFTWARE INSTALLATION**

.. python::

    mamba install -c openalea3 -c conda-forge openalea.ratp

**RATP MODULES**

Here is the list of RATP modules:

- constant_values

- grid3D

- skyvault

- vegetation_types

- micrometeo

- dir_interception

- hemi_interception

- shortwave_balance

- energy_balance

- photosynthesis

  1. *module constant_values*

This module is aimed at setting values for physical constants.

Variables associated to the module **constant_values** are physical
constants

- real :: rho air density (g m\ :sup:`-3`)

- real :: lambda water vaporisation energy (J g\ :sup:`-1`)

- real :: sigma Stephan-Boltzman constant (W m\ :sup:`-2` K\ :sup:`-4`)

- real :: cp heat capacity of the air (J g\ :sup:`-1`)

- real :: gamma psychrometric constant (Pa K\ :sup:`-1`)

- real :: r perfect gaz constant (J K\ :sup:`-1`)

The module **constant_values** contains the subroutine **cv_set**, which
sets the values of the physical constants.

rho=1184 g m\ :sup:`-3`

lambda=2436 J g\ :sup:`-1`

sigma=5.67e-8 W m\ :sup:`-2` K\ :sup:`-4`

cp=1.01 J g\ :sup:`-1`

gamma=66.5 Pa K\ :sup:`-1`

r=8.3143 J K\ :sup:`-1`

Syntax for calling subroutine **cv_set** in OpenAlea environment is:

Ratp.constant_values.cv_set()

2. *module grid3D*

This module is aimed at building a 3D grid, namely the spatial
distribution of leaf area in the voxels.

Variables associated to the module **grid3D** are:

- Grid parameters

- Soil surface parameters

- Canopy structure parameters

Grid parameters are:

- integer njx, njy, njz number of grid voxels along X Y and Z axis

- real dx, dy voxel size according to X- and Y- axis (m)

- real allocatable :: dz(jz) voxel size according to Z- axis, for each
  layer jz

- real :: xorig, yorig, zorig 3D grid origin (m)

- real :: latitude, longitude, timezone

- real :: orientation angle (°) between axis X+ and North

- integer :: idecaly offset between canopy units along Y-axis

The grid is a canopy unit divided into **njz** horizontal layers, and
**njx** and **njy** vertical slices along X- and Y-axis, respectively.
X-axis is the reference axis in the horizontal plane, as defined by the
user (e.g. row direction, North or South axis). Z-axis points downwards,
i.e. horizontal layers are numbered from 1 at the top of the canopy to
**njz**, at the bottom of the canopy. The soil surface is arbitrarily
defined as horizontal layer **njz+1**. Thickness of vertical slices is a
constant defined for X- and Y-axis: **dx** and **dy**, respectively.
Thickness is given for each horizontal layer (1…njz), in variable
**dz(jz), jz=1,njz**. The 3D grid origin co-ordinates (**xorig, yorig,
zorig**) are the origin co-ordinates of the voxel in slice #1 along X-
and Y-axis, at soil surface. **Latitude** (°), **longitude** (°) and
**timezone** (hours) are used to compute the sun direction. **Timezone**
is defined as the lag time between Greenwich and local time, i.e. -2 in
Summer in France.

Soil surface parameters are:

- integer nsol number of soil surface zones

- real rs(2) soil reflectance in PAR and NIR bands

- real total_ground_area total ground area of the scene

The number of soil surface zones in the canopy unit is simply the
product of **njx** and **njy**.

Canopy structure parameters, i.e. parameters of the vegetated grid are:

- integer nveg number of vegetated voxels

- integer nent number of vegetation types in the 3D grid

- integer nemax maximum number of vegetation types in a single voxel
  (nemax < nent)

- real s_vt_vx(je,k) Leaf area (m²) of je\ :sup:`th` vegetation type in
  voxel k

- real s_vx(k) Leaf area (m²) in voxel k

- real s_vt(jent) Leaf area (m²) of vegetation type jent

- real s_canopy Leaf area (m²) of total canopy

- real volume_canopy cumulative volume (m\ :sup:`3`) of vegetated voxels

- real n_canopy average nitrogen content (g m\ :sup:`-2`)

- integer kxyz(jx,jy,jz) voxel index (as a function of location jx, jy,
  jz in the 3D grid)

- integer numx(k) voxel x-coordinate of voxel k

- integer numy(k) voxel y-coordinate of voxel k

- integer numz(k) voxel z-coordinate of voxel k

- integer nje(k) number of vegetation types in voxel of voxel k

- integer nume(je,k) vegetation type of je\ :sup:`th` vegetation type in
  voxel k

- real leafareadensity(je,k) leaf area density of je\ :sup:`th`
  vegetation type in voxel k

- real n_detailed(je,k) nitrogen content (g m\ :sup:`-2`) of
  je\ :sup:`th` vegetation type in voxel k

The module **grid3D** contains 4 subroutines:

- g3d_read: read the 3D grid (i.e. empty grid) parameters from a file.

- g3d_create: create the empty 3D grid from a minimum set of parameters,
  to be further filled from PlantGeom data.

- g3d_fill: fill the 3D empty grid from a file containing canopy
  structure data.

- g3d_destroy: deallocates allocatable arrays of module **grid3D**.

Subroutine **g3d_read** reads the 3D grid parameters from a text file.
Appendix 1 gives an example of the format of such a file. Subroutine
**g3d_read** uses the argument **spec**, which is a string giving the
suffix of the input file. Input file name must be: **grid3D.<spec>**.
Syntax for calling it in the OpenAlea environment is:

SPEC="PP1" # define a simulation by file suffix, here "PP1"

Ratp.grid3d.g3d_read(SPEC) # create the empty 3D grid from parameters
found in file grid3D.PP1

At this stage, allocatable arrays of canopy structure are over-allocated
to **nent** for the number of vegetation types (instead of **nemax**),
and to **njx*njy*njz** (i.e. the total number of voxels in the 3D grid)
(instead of **nveg**). Canopy structure arrays are set to zero.

Subroutine **g3d_create** makes an empty 3D grid from the number of
vertical slices (along X- and Y-axis) and horizontal layers and from a
constant voxel size for each X- Y- and Z-direction. It is devoted to be
used before filling the 3D grid from PlantGeom data. Syntax for calling
it in OpenAlea environment is e.g.:

njx = 2

njy = 3

njz = 4

size_box_x = 4. # meters

size_box_y = 5. # meters

size_box_z = 3.75 # meters

Ratp.grid3d.g3d_create(njx,njy,njz,size_box_x,size_box_y,size_box_z)

Other grid parameters are set to default values, which are:

xorig = 0. 3D grid origin

yorig = 0.

zorig = 0.

latitude = 45. latitude (°)

longitude = 0. longitude (°)

timezone= -2. summer time in France (-2 hours)

orientation = 0. angle (°) between axis X+ and North

idecaly = 0 offset between canopy units along Y-axis

nent=1 nent: number of vegetation types in the 3D grid

nemax=1 nemax: maximum number of vegetation types in a voxel

Like in subroutine **g3d_read**, allocatable arrays of canopy structure
are over-allocated to **nent** for the number of vegetation types
(instead of **nemax**), and to **njx*njy*njz** (i.e. the total number of
voxels in the 3D grid) (instead of **nveg**). Canopy structure arrays
are set to zero, except **n_detailed** which is set to 2.

Subroutine **g3d_fill** fills the empty 3D grid from information found
in a text file. It namely computes canopy structure variables as defined
above. Subroutine **g3d_fill** uses the argument **spec**, which is a
string giving the suffix of the input file, and an integer (equal to 1
or 2) according to the chosen way to fill the 3D grid:

1. From a file where each line gives vegetation type, spatial
   co-ordinates (m), area (cm²) and nitrogen content (g m\ :sup:`-2`) of
   each vegetation element. Appendix 2 gives the format of such a file.
   In this case, the file name must be **digital.<spec>**.

2. From a file where each line gives leaf area density of a given
   vegetation type in a given voxel. Appendix 3 gives the format of such
   a file. In this case, the file name must be **leafarea.<spec>**.

Before running subroutine **g3d_fill**, the empty grid must have been
created, by using either subroutine **g3d_read** or **g3d_create**.
Syntax for calling subroutine **g3d_fill** in the OpenAlea environment
is, e.g:

Ratp.grid3d.g3d_fill(“PP1”,1) # fill the 3D grid from information found
in file digital.PP1

*or*

Ratp.grid3d.g3d_fill(“PP1”,2) # fill the 3D grid from information found
in file leafarea.PP1

The outputs of subroutine **g3d_fill** are canopy structure variables,
as defined above. Vegetated voxels are numbered in an arbitrary way,
from 1 to **nveg**. Empty voxels are not numbered. Each vegetated voxel
**k** is referred by its position in the 3D grid, namely variables
**numx**, **numy**, **numz**, i.e. along X-, Y-, and Z-axis. Conversely
variable **kxyz** gives the voxel # as a function of its position in the
voxel grid. Variable **nje(k)** gives the number of vegetation types in
voxel **k**, while variable **nume(je,k)** indicates the # of
**je**\ :sup:`th` vegetation type in voxel **k**. Leaf area is computed
at several levels in variables **s\_**, while leaf area density
**leafareadensity** is computed at voxel scale for each vegetation type
included in the voxel.

Subroutine **g3d_destroy** deallocates memory used by allocated arrays.
Syntax in OpenAlea environment is:

Ratp.grid3d.g3d_destroy()

3. *module skyvault*

This module is aimed at creating the skyvault, namely discretising the
sky vault as a set of solid angles characterised by their central
direction.

Variables associated to the module **skyvault** are:

- integer ndir Number of directions used for sky discretisation

- real hmoy(jdir) Elevation angle of direction jdir

- real azmoy(jdir) Azimuth angle of direction jdir

- real omega(jdir) Solid angle associated to direction jdir

- real pc(jdir) Relative contribution of direction jdir to incident
  diffuse radiation

The module **skyvault** contains 2 subroutines:

- sv_read: read the sky vault discretisation parameters from a file.

- sv_destroy: deallocates allocatable arrays of module **skyvault**.

Subroutine **sv_read** reads the sky vault discretisation parameters
from a text file. Appendix 4 gives an example of the format of such a
file. Subroutine **sv_read** uses the argument **spec**, which is a
string giving the suffix of the input file. Input file name must be:
**skyvault.<spec>**. Syntax for calling it in the OpenAlea environment
is:

SPEC="PP1" # define a simulation by file suffix, here "PP1"

Ratp.skyvault.sv_read(SPEC) # create the skyvault from parameters found
in file skyvault.PP1

The sky vault discretisation consists in **ndir** directions,
characterised by height angle **hmoy**, azimuth angle **azmoy**, solid
angle **omega** associated to the direction in the sky discretisation,
and relative contribution **pc** of the solide angle to incident diffuse
radiation on the horizontal plane. All allocatable arrays are sized to
**ndir**.

Subroutine **sv_destroy** deallocates memory used by allocated arrays in
module **skyvault**. Syntax in OpenAlea environment is:

Ratp.skyvault.sv_destroy()

4. *module vegetation_types*

This module is aimed at defining physical and physiological properties
of each vegetation type included in the 3D scene. This includes leaf
inclination angle distribution, optical properties in a range of
wavebands, parameters of the relationship between leaf boundary
conductance and wind speed, parameters of the stomatal response to
environmental factors according to Jarvis’ model, parameters of the
relationship between Farquhar’s photosynthesis model parameters and leaf
nitrogen content.

More precisely, variables associated to the module **vegetation_types**
are:

- As to leaf angle inclination distribution:

- integer nbinclimax Maximal number of inclination classes

- integer nbincli(jent) Number of inclination classes for vegetation
  type jent

- real distinc(jent,incli) Fraction of leaf area in leaf inclination
  angle class incli for vegetation type jent

Leaf inclination distribution is described as the distribution of leaf
area in leaf angle classes, in fraction of total leaf area, i.e. the sum
of values [**distinc(jent,incli), incli=1…nbincli(jent)**] should be 1.
The number of inclination classes **nbincli(jent)** may be different for
each vegetation type **jent**. **Nbinclimax** is thus the maximum number
of inclination classes found in any vegetation_type file.

- As to optical properties of leaves

- integer nblomax, nblomin Maximal and minimal number of wavelength
  bands in the input file

- integer nblo(jent) Number of wavelenght bands for vegetation type jent

- real rf(jent,iblo) Average value of leaf reflectance and
  transmittance, one value per wavelength band iblo, for vegetation type
  jent

Optical properties of leaves of any vegetation type are described as the
average value of hemispherical leaf reflectance and transmittance,
**rf(jent,iblo)** for a range of wavebands **iblo**. The input file may
contain any number of wavebands **nblo(jent)**, which can be different
for each vegetation type **jent**. **Nblomax** is thus the maximum
number of wavebands found in any vegetation_type file.

**Important**: Transpiration and photosynthesis computations need
solving the radiation balance for the whole solar radiation and for PAR
(Photosynthetically Active Radiation, 400-700 nm), respectively.
Radiation balance is solved by roughly splitting the whole solar
spectrum into two broad wavebands, PAR and NIR (Near Infra Red
radiation, >700 nm). **In case of transpiration and photosynthesis
computations, wavebands #1 and #2 must be used for PAR and NIR,
respectively.** If **nblomin** **is lesser than 2** (this means that at
least optical properties of one vegetation type are characterised by
**nblo(jent)** < 2), **transpiration and photosynthesis computations are
denied.**

- As to leaf boundary layer conductance ga:

- real aga(jent,2) Parameters of the relationship between leaf boundary
  layer conductance (m s\ :sup:`-1`) and wind speed (m s\ :sup:`-1`),
  for vegetation type jent.

Leaf boundary layer conductance ga (m s\ :sup:`-1`) is computed from as
a linear function of windspeed: ga: ga = **aga(jent,1)**\ \* wind_speed
+ **aga(jent,2)**. Parameters aga can be defined for each vegetation
type.

- As to leaf stomatal conductance gs(s m\ :sup:`-1`): parameters of
Jarvis’ model.

- real agsn(jent,2) effect of leaf nitrogen: gs = A1*Na (g m\ :sup:`-2`)
  + A2

- integer i_gspar(jent) effect of leaf PAR irradiance: gs = f(PAR, µmol
  m\ :sup:`-2` s\ :sup:`-1`)

- real agspar(jent,10)

- integer i_gsca(jent) effect of air CO2 partial pressure: gs = f(CA,
  Pa)

- real agsca(jent,10)

- integer i_gslt(jent) effect of leaf temperature: gs = f(LT, °C)

- real agslt(jent,10)

- real agsvpd(jent,3) effect of leaf VPD: gs=A1*VPD (Pa)+A2, plus
  threshold value.

At present, stomatal conductance of the lower side of the leaf is
modelled from Jarvis’ model, by combining – multiplying – the effect of
several variables. The effect of stomatal conductance acclimation to
light environment is indirectly computed from leaf nitrogen content –
since the latter is closely to time-integrated leaf irradiance – with a
linear relationship using parameters **agsn**.

The effect of leaf PAR irradiance, leaf temperature, and CO\ :sub:`2`
partial pressure in the air is modelled as an empirical function, with
parameters **agspar**, **agslt** and **agsca**, respectively. The
empirical function can be defined from index **i_gspar**, **i_gslt** and
**i_gsca**, respectively. At present, only the following functions are
implemented:

- i_gsXX=1 corresponds to a 2\ :sup:`nd` order polynomial function:

gs = agsXX(jent,1)*XX²+agsXX(jent,2)*XX+agsXX(jent,3)

where **XX** equals **par**, **lt** and **ca** for responses to PAR
irradiance, leaf temperature and CO\ :sub:`2` partial pressure in the
air, respectively.

- i_gsPAR=2 corresponds to a hyperbola function::

gs = [agsPAR(jent,1)*PAR + agsPAR(jent,2)]/ [agsPAR(jent,3)*PAR +
agsPAR(jent,4)]

This function can be used only for response to PAR since the hyperbola
function is inadequate for responses to leaf temperature and
CO\ :sub:`2` partial pressure.

The effect of air VPD is modelled as a linear response, with parameters
**agsvpd**. This linear response allows the RATP model to analytically
solve coupling between stomatal conductance and VPD in the leaf boundary
layer. For VPD values below the threshold value – **agsvpd(jent,3)** –
gs = constant = agsvpd(jent,1)*agsvpd(jent,3)+agsvpd(jent,2). This
allows to shape the response with a plateau at low VPD values.

- As to leaf photosynthesis: parameters of Farquhar’s model.

- real avcmaxn(jent,2) effect of leaf nitrogen on Vcmax at 25°C:

- real ajmaxn(jent,2) effect of leaf nitrogen on Jmax at 25°C:

- real ardn(jent,2) effect of leaf nitrogen on dark respiration at 25°C:

Leaf photosynthesis properties are characterised by Farquhar’s model
parameters: maximum carboxilation rate Vcmax, maximum electron transfert
rate Jmax, dark respiration rate, all at 25°C. They are computed as a
linear function of leaf nitrogen content Na (g m\ :sup:`-2`):

- Vcmax25° (µmol CO2 m\ :sup:`-2` s\ :sup:`-1`) =
  **avcmaxn(jent,1)**\ \*Na + **avcmaxn(jent,2)**

- Jmax25° (µmol e m\ :sup:`-2` s\ :sup:`-1`) = **ajmaxN(jent,1)**\ \*Na
  + **ajmaxn(jent,2)**

- Rd25° (µmol CO2 m\ :sup:`-2` s\ :sup:`-1`) = **ardn(jent,1)**\ \*Na +
  **ardn(jent,2)**

Note that other parameters of the Farquhar’s model are assumed not to be
vegetation type – dependent. This is the reason why they are input
elsewhere (see module **photosynthesis**).

The module **vegetation_types** contains 2 subroutines:

- vt_read: read the vegetation properties from a set of files.

- vt_destroy: deallocates allocatable arrays of module
  **vegetation_types**.

Subroutine **vt_read** reads the parameters defining vegetation
properties from a set of files, i.e. one file per vegetation type. The
names of the vegetation_type files are given in a file called
**vegetation.<spec>**, where spec is a string giving the suffix of the
input file. Appendix 5 gives an example of the format of such a
**vegetation.<spec>** file. Names of vegetation properties files are
free. Appendix 6 gives an example of the format of a vegetation_type
file. Syntax for calling subroutine **vt_read** in the OpenAlea
environment is:

SPEC="PP1" # define a simulation by file suffix, here "PP1"

nvt = Ratp.grid3d.nent # number of vegetation types in the 3D grid.

Ratp.vegetation_types.vt_read(nvt,SPEC) # read vegetation parameters,
from **nvt** files, the name of which is found in file vegetation.PP1.

Note that this way makes all vegetation types included in the 3D grid be
defined in a single run of subroutine **vt_read**, although data for
each vegetation type are in a separate file.

Subroutine **vt_destroy** deallocates memory used by allocated arrays in
module **vegetation_types**. Syntax in OpenAlea environment is:

Ratp.vegetation_types.vt_destroy()

5. *module micrometeo*

This module is aimed at setting the micrometeorological environment
experienced by the 3D scene.

Variables associated to module **micrometeo** are:

- real day,hour

- real glob(iblo) Incident global radiation in band iblo

- real diff(iblo) Incident diffuse radiation in band iblo

- real direct(iblo) Incident direct radiation in band iblo

- real dsg(iblo) D/G ratio in band iblo

- real ratmos Atmospheric radiation (W m\ :sup:`-2`)

- real tsol Soil temperature (°C)

- real taref Air temperature within canopy (°C)

- real earef Water vapour pressure in the within-canopy air (Pa)

- real caref CO\ :sub:`2` partial pressure in the air (Pa)

- real uref(jz) Wind speed (m s\ :sup:`-1`), in each horizontal layer jz

**Day** and **hour** are used to compute the sun direction. All
radiation variables are expressed in W m\ :sup:`-2`. Remember that, in
transpiration and photosynthesis modules, wavebands #1 and #2 refer to
PAR and NIR radiation, respectively.

The module **micrometeo** contains 2 subroutines:

- mm_read: reads micrometeorological data from a file.

- mm_destroy: deallocates allocatable arrays of module
  **vegetation_types**.

Subroutine **mm_read** reads micrometeorological data from a file, where
each line accounts for a time step. Subroutine **mm_read** uses two
arguments: argument **spec** is a string giving the suffix of the input
file. Input file name must be: **mmeteo.<spec>**. Appendix 7 gives an
example of the format of a **mmeteo.<spec>** file. Argument **ntime** is
the time step, i.e. the data line to be read in the file. Syntax for
calling it in the OpenAlea environment is:

SPEC="PP1" # define a simulation by file suffix, here "PP1"

ntime=2 # integer time_step

Ratp.micrometeo.mm_read(SPEC,ntime) # read meteo data, at data line
**ntime** in file mmeteo.PP1

Syntax for calling subroutine **mm_destroy** in the OpenAlea environment
is:

Ratp.micrometeo.mm_destroy()

6. *module dir_interception*

This module is aimed at computing directional radiation interception in
a vegetated 3D grid where several vegetation types are included. This
needs a vegetated grid to have been created and filled with vegetation,
a sky direction to be defined and vegetation parameters – namely leaf
inclination distribution- to have been set. User-useful outputs are STAR
values (Silhouette to Total Area Ratio) and sunlit and shaded leaf area
for the studied direction, as computed from Beer’s law, at different
scales.

Other outputs are computed because they are needed to solve the
radiation balance: they include coefficients of radiation interception,
expressed as exchange coefficients between radiation sources and
radiation receivers. For incident radiation, radiation source is a sky
direction and receivers are vegetation types in voxels and soil surfaces
areas. For scattered radiation, radiation sources are vegetation types
in voxels and soil surface areas, while receivers are the same plus the
sky which receives reflected radiation. Exchange coefficients are
computed from the application of Beer’s law in the sequence of voxels
crossed by the beams. Directional distribution of scattered radiation on
phytoelements is computed from a very simple phase function (for further
details, see Sinoquet and Bonhomme, 1992. Modeling radiative transfer in
mixed and row intercropping systems. Agricultural and Forest
Meteorology, 62, 219-240.).

Input parameters in module **dir_interception** are:

- real dpx, dpy beam spacing along X- and Y- axis (m)

- logical scattering True if scattering variables must be computed

Output variables computed in module **dir_interception** are:

- real star_vt_vx(je,k) STAR at voxel and vegetation type scale

- real star_vx(k) STAR at voxel scale (ie, summing up on vegetation
  types included in the voxel)

- real star_vt(je) STAR at vegetation type scale (ie, summing up on
  voxels)

- real :: star_canopy STAR at canopy scale (ie, summing up on vegetation
  types and voxels)

- real s_detailed(0:1,je,k) Shaded (i=0) and sunlit (i=1) leaf area of
  je\ :sup:`th` vegetation type, in voxel k

- real s_ss_vt(0:1,jent) Shaded (i=0) and sunlit (i=1) leaf area of
  vegetation type jent, i.e. summing up shaded or sunlit are on voxels

- real :: s_ss(0:1) Shaded (i=0) and sunlit (i=1) leaf area in canopy,
  i.e. summing up shaded or sunlit area on voxels and vegetation types

Other variables are associated with module **dir_interception**, which
are used to solve the radiation balance, are given in Appendix 8.

Note that this module deals with **directional interception**, so that
**output values are computed for the studied direction**. A set of beams
are pushed in the 3D grid, which are spaced from **dpx** and **dpy** m
along the X- and Y-axis, respectively.

STAR values are computed at different scales in variables:
**star_vx_vt(je,k)** for **je**\ :sup:`th` vegetation type in voxel
**k**, **star_vx(k)** for voxel **k**, **star_vt(jent)** for vegetation
type **jent** (i.e. summed up on all vegetated voxels), and
**star_canopy** at canopy scale.

Sunlit and shaded leaf area are computed at different scales in
variables: **s_detailed(0 or 1, je, k)** for **je**\ :sup:`th`
vegetation type in voxel **k**, **s_ss_vt(0 or 1, jent)** for vegetation
type **jent** (i.e. summed up on all vegetated voxels), and **s_ss(0 or
1)** at canopy scale. Index #1 set at 0 or 1 refers to shaded or sunlit
area, respectively.

Exchanges coefficients of scattered radiation are computed if Boolean
variable **scattering** is set to **True**. Variable **scattering** must
be set to **True** for further computation of the radiation balance.

The module **dir_interception** includes 2 subroutines available to
users:

- di_doall: computes directional interception properties of the
  vegetated 3D grid.

- di_destroy: deallocates allocatable arrays of module
  **dir_interception**.

Subroutine **di_doall** computes directional interception by vegetation
types in the 3D grid, including incident and scattered radiation. Syntax
for calling subroutine **di_doall** in the OpenAlea environment is e.g.

elevation = Ratp.skyvault.hmoy[1] # Set elevation angle

azimuth = Ratp.skyvault.azmoy[1] # Set azimuth angle

solid_angle = Ratp.skyvault.omega[1] # Set solid angle

dpx = Ratp.grid3d.dx / 5. # Set beam spacing along X-axis

dpy = Ratp.grid3d.dy / 5. # Set beam spacing along Y-axis

# No computation of exchange coefficients of scattered radiation

Ratp.dir_interception.scattering=False

Ratp.dir_interception.di_doall(elevation,azimuth,solid_angle,dpx,dpy)

Subroutine **di_destroy** deallocates allocatable arrays of module
**dir_interception**. Syntax for calling subroutine **di_destroy** in
the OpenAlea environment is:

Ratp.dir_interception.di_destroy()

7. *module hemi_interception*

This module is aimed at computing hemispherical radiation interception
in a vegetated 3D grid where several vegetation types are included, by
summing up directional interception as computed from module
**dir_interception**. This needs a vegetated grid to have been created
and filled with vegetation, a skyvault to have been created and
vegetation parameters – namely leaf inclination distribution- to have
been set. User-useful outputs are STAR values integrated over the sky
hemisphere, as computed from Beer’s law, at different scales.

Other outputs are computed because they are needed to solve the
radiation balance: they include hemisphere-integrated coefficients of
radiation interception, expressed as exchange coefficients between
radiation sources and radiation receivers, both for incident diffuse and
scattered radiation (for further details, see Sinoquet and Bonhomme,
1992. Modeling radiative transfer in mixed and row intercropping
systems. Agricultural and Forest Meteorology, 62, 219-240.).

Output variables computed in module **hemi_interception** are:

- real starsky_vt_vx(je,k) Skyvault-integrated STAR at voxel and
  vegetation type scale

- real starsky_vx(k) Skyvault-integrated STAR at voxel scale (ie,
  summing up on vegetation types included in the voxel)

- real starsky_vt(jent) Skyvault-integrated STAR at vegetation type
  scale (ie, summing up on voxels)

- real starsky_canopy Skyvault-integrated STAR at canopy scale (ie,
  summing up on vegetation types and voxels)

Other variables are associated with module **hemi_interception**, which
are used to solve the radiation balance, are given in Appendix 9.

Note that this module deals with **hemispherical interception**, so that
**output values are computed for the whole skyvault hemisphere**.

Skyvault-integrated STAR values are computed at different scales in
variables: **starsky_vt_vx(je,k)** for **je**\ :sup:`th` vegetation type
in voxel **k**, **starsky_vx(k)** for voxel **k**, **starsky_vt(jent)**
for vegetation type **jent** (i.e. summed up on all vegetated voxels),
and **starsky_canopy** at canopy scale.

The module **hemi_interception** includes 2 subroutines available to
users:

- hi_doall: computes directional interception properties of the
  vegetated 3D grid.

- hi_destroy: deallocates allocatable arrays of module
  **dir_interception**.

Subroutine **hi_doall** computes hemispherical interception by
vegetation types in the 3D grid, including incident and scattered
radiation, from directional interception computation by using module
**dir_interception**. Syntax for calling subroutine **hi_doall** in the
OpenAlea environment is e.g.

Ratp.hemi_interception.hi_doall()

**Important**: Subroutine **hi_doall** must be used:

- after a vegetated grid, a skyvault and vegetation properties have been
  set.

- before the module **shortwave_balance** be used, since the latter
  needs hemispherical exchanges coefficients computed from subroutine
  **hi_doall** to solve the shortwave radiation balance. For this
  reason, subroutine **hi_doall** sets variable scattering to TRUE.

Subroutine **hi_destroy** deallocates allocatable arrays of module
**hemisperical_interception**. Syntax for calling subroutine
**hi_destroy** in the OpenAlea environment is:

Ratp.hemi_interception.hi_destroy()

8. *module shortwave_balance*

Module **shortwave_balance** computes radiation balance from:

- canopy structure of the 3D scene, as described by the 3D array of
  voxels, further expressed in terms of exchange coefficients between
  radiation sources and receivers.

- incident radiation above the canopy, namely the sun direction and
  global and diffuse radiation above the canopy in each waveband.

- physical properties of vegetation, namely leaf inclination
  distribution and optical properties in each waveband

This is the reason why prerequisites before using module
**shortwave_balance** are:

- A 3D grid must be created and filled with phytoelements (see module
  **grid3D**)

- A skyvault must be created (see module **skyvault**)

- Vegetation type parameters must be set (see module
  **vegetation_types**)

- Micrometeorological data must be set (see module **micrometeo**)

- Hemispherical exchanges coefficients for both incident diffuse and
  scattered radiation must be computed (see module
  **hemi_interception**)

Output variables computed by module **shortwave_balance** are:

- real hdeg,azdeg Sun height and azimuth, in degrees.

- real ra_detailed(iblo,0 or 1,je,k) Absorbed radiation by shaded (i=0)
  and sunlit (i=1) leaf area in waveband iblo, for je\ :sup:`th`
  vegetation type in voxel k

- real parirrad(0 or 1,je,k) PAR irradiance of shaded (i=0) and sunlit
  (i=1) leaf area, for je\ :sup:`th` vegetation type in voxel k.

- real swra_detailed(0 or 1,je,k) Solar absorbed radiation of shaded
  (i=0) and sunlit (i=1) leaf area, for je\ :sup:`th` vegetation type in
  voxel k

- real rareflected(iblo) Canopy reflectance of the whole scene, in
  waveband iblo

- real ratransmitted(iblo) Canopy transmittance of the whole scene, in
  waveband iblo

- real raefficiency_vt(iblo,jent) Radiation absorption efficiency of
  vegetation type jent in waveband iblo, i.e. by summing up on voxels.

Absorbed radiation variables **ra_detailed(iblo,0 or 1, je, k)** and
**swra_detailed(0 or 1, je, k)** are expressed in W per m² leaf area of
vegetation type **je** in voxel **k**. Variable **parirrad(0 or 1, je
,k)** is leaf irradiance of vegetation type **je** in voxel **k**,
expressed in µmol PAR s\ :sup:`-1` per m² leaf area. At canopy scale,
variables **rareflected(iblo)**, **ratransmitted(iblo)** and
**raefficiency_vt(iblo,jent)** are dimensionless.

The module **shortwave_balance** includes 2 subroutines available to
users:

- swrb_doall: computes the radiation balance of the 3D scene.

- swrb_destroy: deallocates arrays of module **shortwave_balance**.

Subroutine **swrb_doall** first computes the sun direction from time and
3D grid information, then computes radiation interception from the sun
direction – by using module **dir_interception**), and finally solves
the radiation balance in each waveband. For further details about
computation method, see Sinoquet and Bonhomme, 1992. Modeling radiative
transfer in mixed and row intercropping systems. Agricultural and Forest
Meteorology, 62, 219-240. Syntax for calling subroutine **swrb_doall**
in the OpenAlea environment is simply:

Ratp.shortwave_balance.swrb_doall()

However do not forget that subroutine **swrb_doall** needs a number of
prerequisites, as mentioned above.

Subroutine **swrb_destroy** deallocates arrays of module
**shortwave_balance**. Syntax for calling it in the OpenAlea environment
is:

Ratp.shortwave_balance.swrb_destroy()

9. *module energy_balance*

Module **energy_balance** computes transpiration rates, stomatal
conductance and leaf temperature, in a 3D scene including one or several
vegetation types submitted to micrometeorological variables. Therefore
using module **energy_balance** needs the following prerequisites:

- A 3D grid must be created and filled with phytoelements (see module
  **grid3D**)

- A skyvault must be created (see module **skyvault**)

- Vegetation type parameters must be set (see module
  **vegetation_types**)

- Micrometeorological data must be set (see module **micrometeo**)

- Hemispherical exchanges coefficients for both incident diffuse and
  scattered radiation must be computed (see subroutine **hi_doall** n
  module **hemi_interception**)

- Shortwave radiation balance must be solved (see subroutine
  **swrb_doall** in module **shortwave_balance**).

Output variables computed by module **energy_balance** are:

- real e \_vt_vx (je,k)) Evaporation rate per voxel and vegetation type

- real e_vx(k) Evaporation rate per voxel

- real e_vt(jent) Evaporation rate per vegetation type

- real e_ss_vt(0:1,jent) Evaporation rate of shaded/sunlit area per
  vegetation type

- real e_ss(0:1) Evaporation rate of canopy shaded/sunlit area

- real e_canopy Evaporation rate of canopy

- real h_canopy Sensible heat rate of canopy

- real ts(0:1,je,k) Surface temperature of shaded/sunlit foliage of each
  vegetation type in each voxel

- real rco2(:,:,:) Total leaf resistance to CO\ :sub:`2` transport.

Evaporation rates **e\_...** are all expressed in mmol H\ :sub:`2`\ O
s\ :sup:`-1` per m² leaf area. Leaf temperature **ts** is expressed in
°C. Leaf resistance to CO\ :sub:`2` transfer **rco2** (s m\ :sup:`-1`)
includes the effects of stomatal and leaf boundary layer resistance of
the upper and lower leaf sides.

The module **energy_balance** includes 2 subroutines available to users:

- eb_doall: solves the energy balance of the 3D scene.

- eb_destroy: deallocates arrays of module **energy_balance**.

Subroutine **eb_doall** solves the energy balance of sunlit and shaded
leaf area of each vegetation type in each voxel, by an iterative process
taking into account interactions between leaf temperature, vapour
pressure deficit, stomatal conductance, net radiation balance as
influenced by the leaf and the surrounding vegetation and transpiration
rate. In the present version, **leaf stomatal conductance is computed
after Jarvis’ model**. For further details about computation method,
see: Sinoquet H, Le Roux X, Adam B, Améglio T, Daudet FA, 2001. RATP, a
model for simulating the spatial distribution of radiation absorption,
transpiration and photosynthesis within canopies: application to an
isolated tree crown. Plant Cell and Environment, 24, 395-406. Syntax for
calling subroutine **eb_doall** in the OpenAlea environment is simply:

Ratp.energy_balance.eb_doall()

However do not forget that subroutine **eb_doall** needs a number of
prerequisites, as mentioned above.

Subroutine **eb_destroy** deallocates arrays of module
**energy_balance**. Syntax for calling it in the OpenAlea environment
is:

Ratp.energy_balance.eb_destroy()

10. *module photosynthesis*

Module **photosynthesis** computes assimilation rates by using
Farquhar’s model in a 3D scene including one or several vegetation types
submitted to micrometeorological variables. As Farquhar’s model inputs
are leaf nitrogen content, PAR leaf irradiance, leaf temperature and
leaf resistance to CO\ :sub:`2` transport, using module
**photosynthesis** needs the following prerequisites:

- A 3D grid must be created and filled with phytoelements (see module
  **grid3D**)

- A skyvault must be created (see module **skyvault**)

- Vegetation type parameters must be set (see module
  **vegetation_types**)

- Micrometeorological data must be set (see module **micrometeo**)

- Hemispherical exchanges coefficients for both incident diffuse and
  scattered radiation must be computed (see subroutine **hi_doall** in
  module **hemi_interception**)

- Shortwave radiation balance must be solved (see subroutine
  **swrb_doall** in module **shortwave_balance**), in order to get PAR
  leaf irradiance.

- Energy balance must be solved (see subroutine **eb_doall** in module
  **energy_balance**), in order to get leaf temperature and leaf
  resistance to CO\ :sub:`2` transport.

Output variables computed by module **photosynthesis** are:

- real a_vt_vx(je,k) Assimilation rate per voxel and vegetation type

- real a_vx(k) Assimilation rate per voxel

- real a_vt(jent) Assimilation rate per vegetation type

- real a_ss_vt(:,:) Assimilation rate of shaded/sunlit area per
  vegetation type

- real a_ss(0:1) Assimilation rate of canopy shaded/sunlit area

- real a_canopy Assimilation rate of canopy

Assimilation rates **a\_...** are all expressed in µmol CO\ :sub:`2`
s\ :sup:`-1` per m² leaf area.

Other variables associated to module **photosynthesis** are parameters
of the Farquhar’s model:

- real kc25: Michaelis constant of Rubisco for carboxylation (Pa)

- real ko25: Michaelis constant of Rubisco for oxigenation (Pa)

- real specif25: Rubisco specificity factor (dimensionless)

- real dhakc: activation energy for carboxylation (J mol\ :sup:`-1`)

- real dhako: activation energy for oxigenation (J mol\ :sup:`-1`)

- real dhakspecif: activation energy for Rubisco specificity (J
  mol\ :sup:`-1`)

- real dhakresp: activation energy for dark respiration (J
  mol\ :sup:`-1`)

- real dhavcmax: activation energy for Vcmax (J mol\ :sup:`-1`)

- real dhajmax: activation energy for Jmax (J mol\ :sup:`-1`)

- real dhdvcmax: deactivation energy for Vcmax (J mol\ :sup:`-1`)

- real dhdjcmax: deactivation energy for Jmax (J mol\ :sup:`-1`)

- real dsvcmax: entropy term for Vcmax (J K\ :sup:`-1` mol\ :sup:`-1`)

- real dsjmax: entropy term for Jmax (J K-1 mol-1)

- real alpha: apparent quantum yield (mol electron/ mol photon)

- real o2: partial O2 pressure in the leaf (Pa)

The module **photosynthesis** includes 3 subroutines available to users:

- farquhar_parameters_set: sets parameters of the Farquhar’s model.

- ps_doall: computes assimilation rates from Farquhar’s model.

- ps_destroy: deallocates arrays of module **photosynthesis**.

Subroutine **farquhar_parameters_set** sets Farquhar’s model parameters
at values used in: Le Roux X, Grand S, Dreyer E, Daudet FA, 1999.
Parameterisation and testing of a biochemically-based photosynthesis
model in walnut (Juglans regia L.) trees and seedlings. Tree Physiology,
19, 481-492. These values are given in Appendix 10. Syntax for calling
it in the OpenAlea environment is:

Ratp.photosynthesis.farquhar_parameters_set()

*Important*: Farquhar’s model parameters can also be simply set from the
OpenAlea environment, e.g.:

Ratp.photosynthesis.dhakc=80470. # activation energy for carboxylation
(J mol\ :sup:`-1`)

Subroutine ps_doall computes assimilation rates from Farquhar’s model,
namely variables **a\_...** Syntax for calling it in the OpenAlea
environment is simply:

Ratp.photosynthesis.ps_doall()

However do not forget that subroutine **ps_doall** needs a number of
prerequisites, as mentioned above.

Subroutine **ps_destroy** deallocates arrays of module
**photosynthesis**. Syntax for calling it in the OpenAlea environment
is:

Ratp.photosynthesis.ps_destroy()

**Appendix 1**

Example of input file of 3D grid parameters: grid3D.PP1

16 20 15 ! number of grid voxels along X Y and Z axis

0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25
0.25 0.25 0.25 !\*

0.0 0.0 0.0 ! 3D grid origin

38.7 -8.8 -2. ! latitude, longitude timezone (hours)

0.0 ! angle (°) between axis X+ and North

0 ! offset between canopy units along Y-axis

2 ! number of vegetation entities in the 3D grid

*Caution*: This kind of file does not use a header line.

\*: line #2 contains voxel size according to X- Y- and Z- axis, i.e.
variables dx, dy, (dz(jz),jz=1,njz), i.e. a set of 2+njz values.

**
Appendix 2**

Example of input file of phytoelements co-ordinates and area:
digital.PP1

The file contains one header line, and as many lines as vegetation
elements – e.g. leaves – in the 3D scene. Column #1 contains vegetation
type, columns #2 to 4 contain x-, y- z- co-ordinates (cm), column #5
contains area (cm²) and column #6 contains leaf nitrogen content (g
m\ :sup:`-2`). This sequence of columns is mandatory.

Z-co-ordinate must be negative, i.e. as usual when using a 3D digitiser
to record organ co-ordinates.

#vt x (cm) y (cm) z (cm) area N (g m\ :sup:`-2`) Peach tree, Lisbon 1998

1 210 48 -60 22 2

1 208 46 -56 22 2

1 205 45 -52 22 2

1 204 44 -52 22 2

1 204 44 -52 22 2

1 201 42 -54 22 2

1 199 40 -55 22 2

1 197 39 -55 22 2

…

**
Appendix 3**

Example of input file of vegetated voxels: leafarea.PP1

The file contains one header line, and as many lines as vegetation types
– e.g. species – in vegetated voxels. Column #1 to 3 contain x-, y- z-
voxel co-ordinates (as integers), column #4 contains vegetation type,
column #5 contains leaf area density of this vegetation type in this
voxel (m\ :sup:`2` m\ :sup:`3`) and column #6 contains leaf nitrogen
content (g m\ :sup:`-2`) of this vegetation type in this voxel. This
sequence of columns is mandatory.

#voxel_x #voxel_y #voxel_z #vt LAD (m\ :sup:`2` m\ :sup:`3`) N (g
m\ :sup:`-2`)

1 1 1 1 2.5 2.0

1 1 1 2 2.5 2.0

1 1 2 1 2.5 2.0

1 1 2 2 2.5 2.0

1 1 4 1 2.5 2.0

1 1 4 1 2.5 2.0

…

*Caution*: Voxels which are not included in the input are assumed not to
contain vegetation.

**
Appendix 4**

Example of input file of sky vault discretisation: skyvault.PP1

The file contains ndir + 1 lines, i.e. one line with the number of
directions used for sky discretisation – ndir – and one line per sky
direction. Sky direction lines contains 4 columns: elevation angle (°),
azimuth angle (°), solid angle associated with direction (sr), fraction
of incident diffuse radiation coming from the solid angle.

The following file holds for sky discretisation according to a
46-directions turtle (den Dulk, 1989) with a Standard Over-Cast sky
distribution (Walsh, 1961).

46 ! number of directions used for sky discretisation

9.23 12.23 .1355 .0043

9.23 59.77 .1355 .0043

9.23 84.23 .1355 .0043

9.23 131.77 .1355 .0043

9.23 156.23 .1355 .0043

9.23 203.77 .1355 .0043

9.23 228.23 .1355 .0043

9.23 275.77 .1355 .0043

9.23 300.23 .1355 .0043

9.23 347.77 .1355 .0043

10.81 36.00 .1476 .0055

10.81 108.00 .1476 .0055

10.81 180.00 .1476 .0055

10.81 252.00 .1476 .0055

10.81 324.00 .1476 .0055

26.57 .00 .1207 .0140

26.57 72.00 .1207 .0140

26.57 144.00 .1207 .0140

26.57 216.00 .1207 .0140

26.57 288.00 .1207 .0140

31.08 23.27 .1375 .0197

31.08 48.73 .1375 .0197

31.08 95.27 .1375 .0197

31.08 120.73 .1375 .0197

31.08 167.27 .1375 .0197

31.08 192.73 .1375 .0197

31.08 239.27 .1375 .0197

31.08 264.73 .1375 .0197

31.08 311.27 .1375 .0197

31.08 336.73 .1375 .0197

47.41 .00 .1364 .0336

47.41 72.00 .1364 .0336

47.41 144.00 .1364 .0336

47.41 216.00 .1364 .0336

47.41 288.00 .1364 .0336

52.62 36.00 .1442 .0399

52.62 108.00 .1442 .0399

52.62 180.00 .1442 .0399

52.62 252.00 .1442 .0399

52.62 324.00 .1442 .0399

69.16 .00 .1378 .0495

69.16 72.00 .1378 .0495

69.16 144.00 .1378 .0495

69.16 216.00 .1378 .0495

69.16 288.00 .1378 .0495

90.00 180.00 .1196 .0481

**
Appendix 5**

Example of input file defining vegetation type files to be used:
vegetation.PP1

The file contains one line per vegetation type, with vegetation type #
and the name of the file containing vegetation parameters.

1 Planophile_walnut.veg

2 Planophile_walnut.veg

3 Planophile_walnut.veg

…

**
Appendix 6**

Example of input file describing vegetation parameters:
Planophile_walnut.veg

**Caution**: There must be one file per vegetation type.

9 ! Number of leaf inclination angle classes

0.220 0.207 0.182 0.149 0.111 0.073 0.040 0.015 0.003 ! e.g. planophile
distr.

2 ! Number of wavelength bands

0.085 0.425 ! scattering coefficients in PAR and NIR wavebands

0.01 0.0071 ! Boundary layer conductance: ga = A1 wind_speed + A2
:sup:`(1)`

2.002e-3 0.740e-3 ! Jarvis’ model: effect of leaf N content: gsmax = A1
Na + A2 :sup:`(1)`

1 3 -3.752e-7 1.1051e-3 0.183 ! Jarvis model: gs/gsmax = f(PAR)
:sup:`(2)`

1 3 2.32e-4 -4.02e-2 2.07 ! Jarvis’ model: gs/gsmax = f(CA) :sup:`(2)`

1 3 -4.82e-3 0.24165 -2.029 ! Jarvis model: gs/gsmax = f(LT) :sup:`(2)`

-1.8e-4 1.18 1000. ! Jarvis model: effect of leaf surface VPD: gs/gsmax
= A1 VPD (Pa) + A2\ :sup:`(3)`

20.0 6. ! Farquhar's model: Vcmax25°C (µmol CO2 m\ :sup:`-2`
s\ :sup:`-1`) = A1 Na (g m\ :sup:`-2`) + A2 :sup:`(1)`

52.0 15. ! Farquhar's model: Jmax25°C (µmol e m\ :sup:`-2` s\ :sup:`-1`)
= A1 Na (g m\ :sup:`-2`) + A2 :sup:`(1)`

0.25 0.05 ! Farquhar's model: Rd25°C (µmol CO\ :sub:`2` m\ :sup:`-2`
s\ :sup:`-1`) = A1 Na (g m\ :sup:`-2`) + A2 :sup:`(1) (4)`

:sup:`(1)`: The line contains parameters A1 and A2.

:sup:`(2)`: The line contains the function # (here, 1 for the
2\ :sup:`nd` order polynomial function), the number of parameters of the
function, and the values of the parameters. Before entering parameters,
remember that PAR is expressed in µmol m\ :sup:`-2` s\ :sup:`-1`, LT
(leaf temperature) is expressed in °C and CA (partial pressure of
CO\ :sub:`2` in the air) is expressed in Pa.

:sup:`(3)`: The line contains parameters A1 and A2, plus threshold value
VPD\ :sub:`t`. For VPD < VPD\ :sub:`t` (here 1000 Pa), gs/gsmax=
constant = A1 VPD\ :sub:`t` + A2.

:sup:`(4)`: Respiration parameters must be entered, so that
**respiration rate is positive**.

**
Appendix 7**

Example of input file of micrometeorological data: mmeteo.PP1

The file contains one header line, then one line per time step. Time
step is defined by time and a set of values for meteorological
variables. For time step lines, the sequence of columns is: day, hour,
incident PAR (W m\ :sup:`-2`), incident diffuse PAR (W m\ :sup:`-2`),
incident NIR (W m\ :sup:`-2`), incident diffuse NIR (W m\ :sup:`-2`),
atmospheric radiation (W m\ :sup:`-2`), soil surface temperature (°C),
air temperature (°C), partial pressure of water vapour in the air (Pa),
partial pressure of CO\ :sub:`2` in the air (Pa), wind speed (m
s\ :sup:`-1`).

Day Hour PARg PARd NIRg NIRd Ra Tsol Tair eair Cair Wind_Speed

190 8.125 216 45 234 48 345 22.8 20.73 1802 35 1.296

190 8.375 239 46 259 50 340 25.2 21.43 1830 35 1.222

190 8.625 263 48 285 52 339 26.6 22.01 1844 35 1.592

190 8.875 285 51 309 55 338 27.5 22.59 1867 35 1.493

190 9.125 306 53 332 57 340 28.5 23.16 1877 35 1.256

190 9.375 327 54 354 58 341 29.8 23.88 1909 35 1.461

190 9.625 347 53 375 58 342 31.5 24.49 1937 35 1.699

190 9.875 366 53 397 58 341 34.3 25.07 1956 35 1.436

…

In case meteorological variables are not all available, the following
approximations can help. The user is however responsible for choosing to
use them:

1. PARg (W m\ :sup:`-2`) = 0.48 Rg (W m\ :sup:`-2`), where Rg is
   incident global solar radiation.

2. PARd / PARg = Rd / Rg, where Rd is incident diffuse solar radiation
   (W m\ :sup:`-2`).

3. NIRg (W m\ :sup:`-2`) = 0.52 Rg (W m\ :sup:`-2`)

4. NIRd / NIRg = Rd / Rg

5. Ra ≈ 300 W m\ :sup:`-2`

6. Tsoil = Tair

7. Cair ≈ 36 Pa

Note that assumption #2 usually underestimates PARd, while assumption #4
overestimates NIRd.

**
Appendix 8**

Intermediate variables associated to module
**directional_interception**:

- real share(je,k) Sharing coefficient of intercepted radiation between
  vegetation_type je included in voxel k (k=1,nveg), for the studied
  direction.

- real xk(k) Optical density of voxel k (k=1,nveg), = somme(Ki*LADi)

- real riv(k) Fraction of directional incident radiation intercepted in
  voxel k (k=1,nveg), for the studied direction.

- real ris(ksol) Fraction of directional incident radiation intercepted
  by ground zone ksol (ksol=1,nsol), for the studied direction.

- real rka(jent) Fraction of scattered radiation in current direction by
  vegetation type jent (jent=1,nent)

- real ffvvb(kr,ks) Exchange coefficients of scattered radiation between
  source vegetated voxels (ks=1,nveg) and receiving vegetated voxels
  (kr=1,nveg), for the studied direction.

- real ffsvb(ksol,ks) Exchange coefficients of scattered radiation
  between source vegetated voxels (ks=1,nveg) and receiving soil surface
  areas (ksol=1,nsol), for the studied direction.

- real ffcvb(ks) Exchange coefficients of scattered radiation between
  source vegetated voxels (ks=1,nveg) and the sky, for the studied
  direction.

- real ffvsb(kr,ksol) Exchange coefficients of scattered radiation
  between soil areas (ksol=1,nsol) and vegetated voxels (kr=1,nveg, for
  the studied direction.

- real ffcsb(ksol) Exchange coefficients of scattered radiation between
  soil surface (ksol=1,nsol) and the sky, for the studied direction.

Note that this module deals with **directional interception**, so that
**output values are computed for the studied direction**. A set of beams
are pushed in the 3D grid, which are spaced from **dpx** and **dpy** m
along the X- and Y-axis, respectively. Sharing coefficient of
intercepted radiation **share(je,k)** is the fraction of intercepted
radiation by voxel **k**, which is intercepted by vegetation type
**je**. As a result, the sum of **[share(je,k), je=1,nje(k)]** equals 1.
If voxel k includes only one vegetation type, **share(1,k)** also equals
1. Optical density **xk(k)** of voxel **k** is the sum – over **nje(k)**
vegetation types included in voxel **k** – of the product of directional
extinction coefficient and leaf area density. The fractions of
directional incident direction **riv(k)** and **ris(k),** intercepted by
voxel **k** and soil surface area **ksol**, respectively, in the studied
direction are expressed in m².

Exchanges coefficients of scattered radiation are computed if Boolean
variable **scattering** is set to .TRUE. Arrays of scattered radiation
exchange coefficients are 1- or 2-dimensional, where 1\ :sup:`st` and
2\ :sup:`nd` index refer to the receiver and the source of radiation,
respectively.

**Appendix 9**

Intermediate variables associated to module
**hemispherical_interception**:

- real rdiv(je,k) Fraction of incident diffuse radiation intercepted by
  j\ :sup:`th` vegetation type in voxel k, k=1,nveg

- real rdis(:) Fraction of incident diffuse radiation intercepted by
  ground_zone ksol, ksol=1,nsol

- real ffvv(:,:,:,:) Exchange coefficient between js\ :sup:`th`
  vegetation type in voxel ks and jr\ :sup:`th` vegetation type in voxel
  kr

- real ffsv(:,:,:) Exchange coefficient between js\ :sup:`th` vegetation
  type in voxel ks and ground_zone ksol

- real ffcv(:,:) Exchange coefficient between js\ :sup:`th` vegetation
  type in voxel ks and sky (i.e. for reflected radiation)

- real ffvs(:,:,:) Exchange coefficient between ground_zone ksol and
  jr\ :sup:`th` vegetation type in voxel kr

- real ffcs(:) Exchange coefficient between ground_zone ksol and sky
  (i.e. for reflected radiation)

**Appendix 10**

Values of Farquhar’s model parameters set by subroutine
**farquhar_parameters_set** in **module photosynthesis**.

Values are those used in: Le Roux X, Grand S, Dreyer E, Daudet FA, 1999.
Parameterisation and testing of a biochemically-based photosynthesis
model in walnut (Juglans regia L.) trees and seedlings. Tree Physiology,
19, 481-492.

**RUBISCO parameters at 25°C**

kc25=27.9 Michaelis constant of Rubisco for carboxylation (Pa)

ko25=41959 Michaelis constant of Rubisco for oxigenation (Pa)

specif25=2311.4 Rubisco specificity factor (dimensionless)

**Activation energy**

dhakc=80470. activation energy for carboxylation (J mol\ :sup:`-1`)

dhako=14510. activation energy for oxigenation (J mol\ :sup:`-1`)

dhaspecif=-28990. activation energy for Rubisco specificity (J
mol\ :sup:`-1`)

dharespd=84450. activation energy for dark respiration (J
mol\ :sup:`-1`)

dhavcmax=109500. activation energy for maximum carboxylation rate, Vcmax
(J mol\ :sup:`-1`)

dhajmax=79500. activation energy for maximum electron transfert rate,
Jmax (J mol\ :sup:`-1`)

**Deactivation energy**

dhdvcmax=199500. deactivation energy for maximum carboxylation rate,
Vcmax (J mol\ :sup:`-1`)

dhdjmax=201000. deactivation energy for maximum electron transfert rate,
Jmax (J mol\ :sup:`-1`)

**Entropy terms**

dsvcmax=650. entropy term for maximum carboxylation rate, Vcmax (J
K\ :sup:`-1` mol\ :sup:`-1`)

dsjmax=650. entropy term for maximum electron transfert rate, Jmax (J
K\ :sup:`-1` mol\ :sup:`-1`)

**Other constant parameters**

alpha=0.24 apparent quantum yield (mol electron mol photon\ :sup:`-1`)

o2=20984. partial O2 pressure in the leaf (Pa)
