!------------------------------------------------------------------------------

!Modele de Photosynthese de Farquhar
!parametre a partir de la conductance stomatique (Jarvis)

module Photosynthesis

! Parameters of the Farquhar's model:
real :: kc25   ! kc25: Michaelis constant of Rubisco for carboxylation (Pa)
real :: ko25   ! ko25: Michaelis constant of Rubisco for oxigenation (Pa)
real :: specif25  ! specif25:  Rubisco specificity factor  (dimensionless)
real :: dhakc   !  dhakc: activation energy for carboxylation (J.mol-1)
real :: dhako   !  dhako: activation energy for oxigenation (J.mol-1)
real :: dhaspecif !  dhakspecif: activation energy for  Rubisco specificity (J.mol-1)
real :: dharespd  !  dhakresp: activation energy for dark respiration (J.mol-1)
real :: dhavcmax  !  dhavcmax: activation energy for maximum carboxylation rate, Vcmax (J.mol-1)
real :: dhajmax  !  dhajmax: activation energy for maximum electron transfert rate, Jmax (J.mol-1)
real :: dhdvcmax  !  dhdvcmax: deactivation energy for maximum carboxylation rate, Vcmax (J.mol-1)
real :: dhdjmax  !  dhdjcmax: deactivation energy for maximum electron transfert rate, Jmax (J.mol-1)
real :: dsvcmax  ! dsvcmax:  entropy term for maximum carboxylation rate, Vcmax (J.K-1.mol-1)
real :: dsjmax  ! dsjmax:  entropy term for maximum electron transfert rate, Jmax (J.K-1.mol-1)
real :: alpha   ! alpha: apparent quantum yield (mol electron/ mol photon)
real :: O2    ! O2 : partial O2 pressure in the leaf (Pa)

! Scaling factors used in the Farquhar's model:
real :: ckc         ! Scaling factor for kc
real :: cko         ! Scaling factor for ko
real :: cspecif        ! Scaling factor for specif
real, allocatable :: cvcmax(:,:)   ! Scaling factor for VCmax, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.
real, allocatable :: cjmax(:,:)   ! Scaling factor for Jmax, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.
real, allocatable :: crespd(:,:)   ! Scaling factor for RespD, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.

real, allocatable :: A_detailed(:,:,:)! Assimilation rate per voxel and vegetation of shaded/sunlit area
real, allocatable :: A_vt_vx(:,:)  ! Assimilation rate per voxel and vegetation type
real, allocatable :: A_vx(:)       ! Assimilation rate per voxel
real, allocatable :: A_vt(:)    ! Assimilation rate per vegetation type
real, allocatable :: A_ss_vt(:,:) ! Assimilation rate of shaded/sunlit area per vegetation type
real ::      A_ss(0:1)      ! Assimilation rate of canopy shaded/sunlit area
real ::      A_canopy         ! Assimilation rate of canopy


contains

 subroutine Farquhar_parameters_set


! Parameters of the Farquhar's model : default values, ie for walnut tree (Le Roux et al. 1999)
!
! RUBISCO PARAMETERS AT 25°C
!
  kc25=27.9   !  kc25: Michaelis constant of Rubisco for carboxylation (Pa)
  ko25=41959   !  ko25: Michaelis constant of Rubisco for oxigenation (Pa)
  specif25=2311.4 !  specif25:  Rubisco specificity factor  (dimensionless)

! ACTIVATION ENERGY

  dhakc=80470.  !     dhakc: activation energy for carboxylation (J.mol-1)
  dhako=14510.  !     dhako: activation energy for oxigenation (J.mol-1)
  dhaspecif=-28990. !     dhakspecif: activation energy for  Rubisco specificity (J.mol-1)
  dharespd=84450. !     dhakresp: activation energy for dark respiration (J.mol-1)
  dhavcmax=109500. !     dhavcmax: activation energy for maximum carboxylation rate, Vcmax (J.mol-1)
  dhajmax=79500.  !     dhajmax: activation energy for maximum electron transfert rate, Jmax (J.mol-1)


! DEACTIVATION ENERGY

  dhdvcmax=199500. !     dhdvcmax: deactivation energy for maximum carboxylation rate, Vcmax (J.mol-1)
  dhdjmax=201000. !     dhdjcmax: deactivation energy for maximum electron transfert rate, Jmax (J.mol-1)

! ENTROPY TERMS

  dsvcmax=650.  !  dsvcmax:  entropy term for maximum carboxylation rate, Vcmax (J.K-1.mol-1)
  dsjmax=650.   !  dsjmax:  entropy term for maximum electron transfert rate, Jmax (J.K-1.mol-1)

! OTHER CONSTANT PARAMETERS

  alpha=0.24   !  alpha: apparent quantum yield (mol electron/ mol photon)
  O2=20984.   !  O2 : partial O2 pressure in the leaf (Pa)


 end subroutine Farquhar_parameters_set


 subroutine Farquhar_scaling_factors

  use constant_values
  use grid3D
  use vegetation_types

  real :: VCmax25  ! maximum carboxylation rate at 25°C
  real :: Jmax25  ! maximum electron transfert rate at 25°C
  real :: Rd25   ! dark respiration rate at 25°C

!  Computation of scaling factors: kc, ko, specificity

  ckc = alog( kc25 / exp(-dhakc/r/298.15) )
  cko = alog( ko25 / exp(-dhako/r/298.15) )
  cspecif = alog( specif25 / exp(-dhaspecif/r/298.15) )

!  Computation of scaling factors: VCmax, Jmax, Rd

  if (allocated(cvcmax)) deallocate(cvcmax) ! Scaling factor for VCmax, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.
  if (allocated(cjmax)) deallocate(cjmax)  ! Scaling factor for Jmax, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.
  if (allocated(crespd)) deallocate(crespd) ! Scaling factor for RespD, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.

  allocate(cvcmax(nemax,nveg))
  allocate(cjmax(nemax,nveg))
  allocate(crespd(nemax,nveg))

  do k=1,nveg
   do je=1,nje(k)
    jent=nume(je,k)

    VCmax25 = AVCmaxN(jent,1) * N_detailed(je,k) + AVCmaxN(jent,1)
    cvcmax(je,k) = alog( VCmax25 / (exp(-dhavcmax/r/298.15)/(1+exp(dsvcmax/r- (dhdvcmax/r/298.15)))) )

    Jmax25 = AJmaxN(jent,1) * N_detailed(je,k) + AJmaxN(jent,1)
    cjmax(je,k) = alog( Jmax25 / (exp(-dhajmax/r/298.15)/(1+exp(dsjmax/r- (dhdjmax/r/298.15)))) )

    Rd25 = ARdN(jent,1) * N_detailed(je,k) + ARdN(jent,1)
    crespd(je,k) = alog( Rd25 / exp(-dharespd/r/298.15) )
   end do
  end do

 end subroutine Farquhar_scaling_factors


 subroutine ps_doall
  use constant_values
  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo
  use shortwave_balance
  use energy_balance

  real :: A, rco2Pa

  call ps_destroy

  call Farquhar_scaling_factors

!  Allocation of module arrays (except arrays of scaling factors allocated in
  allocate(A_detailed(0:1,nemax,nveg))
  allocate(A_vt_vx(nemax,nveg))
  allocate(A_vx(nveg))
  allocate(A_vt(nent))
  allocate(A_ss_vt(0:1,nent))

!  Initialisation of output variables for photosynthesis:
  A_detailed = 0.
  A_vt_vx = 0.  ! Assimilation rate per voxel and vegetation type
  A_vx = 0.       ! Assimilation rate per voxel
  A_vt = 0.    ! Assimilation rate per vegetation type
  A_ss_vt = 0. ! Assimilation rate of shaded/sunlit area per vegetation type
  A_ss = 0.      ! Assimilation rate of canopy shaded/sunlit area
  A_canopy = 0.      ! Assimilation rate of canopy


!  Assimilation rate computation from Farquhar's model applied to shaded/sunlit area of each vegetation type in each voxel

  do k=1,nveg
   do je=1,nje(k)
    jent=nume(je,k)
    do joe=0,1
     rco2Pa=rco2(joe,je,k)*101325. ! Conversion into µmol CO2-1 m2 s Pa
     A=0.
     call Farquhar_model_1(A,crespd(je,k),cvcmax(je,k),cjmax(je,k),rco2Pa,ts(joe,je,k)+273.15,PARirrad(joe,je,k),caref)

     A = A * S_detailed(joe,je,k)  ! Net A rate in µmol CO2 s-1
     A_detailed(joe,je,k) = A
     A_vt_vx(je,k) = A_vt_vx(je,k) + A
     A_vx(k) = A_vx(k) + A
     A_vt(jent) = A_vt(jent) + A
     A_ss_vt(joe,jent) = A_ss_vt(joe,jent) + A
     A_ss(joe) = A_ss(joe) + A
     A_canopy = A_canopy + A
    end do
   end do
  end do

!  Normalisation of A_rates by leaf area

  do k=1,nveg
   do je=1,nje(k)
    A_vt_vx(je,k)=A_vt_vx(je,k)/S_vt_vx(je,k)
   end do
   A_vx(k)=A_vx(k)/S_vx(k)
  end do
  do jent=1,nent
   do joe=0,1
    A_ss_vt(joe,jent)=A_ss_vt(joe,jent)/S_ss_vt(joe,jent)
   end do
   A_vt(jent)=A_vt(jent)/S_vt(jent)
  end do
  do joe=0,1
   A_ss(joe)=A_ss(joe)/S_ss(joe)
  end do
  A_canopy = A_canopy / S_canopy


 end subroutine ps_doall


 subroutine Farquhar_model_1(net_A,crespd0,cvcmax0,cjmax0,rco2Pa,leaf_tempK,leaf_PAR,caref)

 use constant_values

 real :: net_A
 real :: crespd0, cvcmax0, cjmax0
 real :: leaf_tempK, leaf_PAR

 real :: zkc, zko, specif, respd, vcmax, zjmax, zj, wc, wj

 real :: aa, bb, ccc, dd

  zkc=exp(ckc - (dhakc/r/leaf_tempK)) ! Rubisco Michaelis constant for carboxylation Kc (Pa)
  zko=exp(cko - (dhako/r/leaf_tempK)) ! Rubisco Michaelis constant for oxigenation Ko (Pa)
  specif=exp(cspecif - (dhaspecif/r/leaf_tempK)) ! Rubisco specificity
  respd=exp(crespd0-(dharespd/r/leaf_tempK)) ! Dark respiration rate (µmol CO2 m-2 s-1)
  vcmax=exp(cvcmax0-(dhavcmax/r/leaf_tempK))/(1+exp(dsvcmax/r- (dhdvcmax/r/leaf_tempK))) ! Maximum carboxylation rate VCmax (µmol CO2 m-2 s-1)
  zjmax=exp(cjmax0-(dhajmax/r/leaf_tempK))/(1+exp(dsjmax/r- (dhdjmax/r/leaf_tempK)))  ! Maximum electron transfert rate Jmax (µmol e m-2 s-1)

!  Actual electron flux J (µmol e m-2 s-1)
  aa=alpha*leaf_PAR
  zj=aa/sqrt(1+(aa/zjmax)**2)

!  Assimilation rate limited by electron flux,  WJ (µmol CO2 m-2 s-1)
  aa=rco2Pa
  bb=(4.*respd-zj)*rco2Pa/4. - caref - O2/specif
  ccc=zj*(caref/4.-O2/specif/8.)-respd*(caref+O2/specif)
  dd=bb*bb-4.*aa*ccc
  wj=(-bb-sqrt(dd))/(2*aa)

!  Assimilation rate limited by Rubisco,  Wc (µmol CO2 m-2 s-1)
  aa=rco2Pa
  bb=(respd-vcmax)*rco2Pa - caref - zkc*(1+O2/zko)
  ccc=vcmax*(caref-0.5*O2/specif)-respd*(caref+zkc*(1+O2/zko))
  dd=bb*bb-4.*aa*ccc
  wc=(-bb-sqrt(dd))/(2*aa)

!  Actual assimilation rate: min(Wj,Wc)
  net_A=amin1(wj,wc)

 end subroutine Farquhar_model_1


 subroutine ps_destroy

  if (allocated(cvcmax)) deallocate(cvcmax) ! Scaling factor for VCmax, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.
  if (allocated(cjmax)) deallocate(cjmax)  ! Scaling factor for Jmax, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.
  if (allocated(crespd)) deallocate(crespd) ! Scaling factor for RespD, depends on vegetation type# and voxel#, beacuse depends on leaf nitrogen content.

  if (allocated(A_detailed)) deallocate(A_detailed)! Assimilation rate per voxel and vegetation of shaded/sunlit area
  if (allocated(A_vt_vx))  deallocate(A_vt_vx) ! Assimilation rate per voxel and vegetation type
  if (allocated(A_vx))   deallocate(A_vx)      ! Assimilation rate per voxel
  if (allocated(A_vt))   deallocate(A_vt)   ! Assimilation rate per vegetation type
  if (allocated(A_ss_vt))  deallocate(A_ss_vt)! Assimilation rate of shaded/sunlit area per vegetation type

 end subroutine ps_destroy


end module Photosynthesis

!---------------------------------------------------------------
