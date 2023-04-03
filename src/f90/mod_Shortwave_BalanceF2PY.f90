!------------------------------------------------------------------------------

module shortwave_balance

real :: hdeg,azdeg    ! sun height and azimuth, in degrees

real, allocatable :: RA_detailed(:,:,:,:)   ! IBLO_band absorbed radiation of shaded and sunlit leaf area
real, allocatable :: PARirrad(:,:,:)    ! PAR irradiance of shaded and sunlit leaf area
real, allocatable :: SWRA_detailed(:,:,:)   ! Solar absorbed radiation of shaded and sunlit leaf area, ie. summing up wavebands

real, allocatable :: RAreflected(:), RAtransmitted(:) ! Reflected and transmitted fluxes above and below the whole scene, in waveband iblo
real, allocatable :: RAefficiency_vt(:,:)      !  Light absorption efficiency of vegetation type jent in waveband iblo

real, allocatable :: xint1v(:,:), xint1s(:) ! Intercepted flux of incident radiation (1st interception, no scattering) by vegetation type in voxel k, and by ground zone ksol
real, allocatable :: xintav(:,:), xintas(:) ! Intercepted flux of radiation (incident plus scattered) by vegetation type in voxel k, and by ground zone ksol

real, allocatable :: Spar(:,:)     ! Leaf area distribution in PAR classes, for each vegetation type


contains

 subroutine swrb_doall
!  Part 5: Short-wave radiation balance:
!             - For a given time step
!             - Direct radiation interception
!             - Radiation balance for each wave band

  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo

!  Module array allocation and initialisation

  call swrb_destroy

  if (nblosoil.lt.nblomin) then
   nblomin=nblosoil
   !write(*,*) 'Warning: radiation balance will be computed for ', nblosoil,' wavebands'
  endif

  allocate(RA_detailed(nblomin,0:1,nemax,nveg))
  RA_detailed=0.
  allocate(SWRA_detailed(0:1,nemax,nveg))
  SWRA_detailed=0.
  allocate(PARirrad(0:1,nemax,nveg))
  PARirrad=0.

  allocate(RAreflected(nblomin))
  RAreflected=0.
  allocate(RAtransmitted(nblomin))
  RAtransmitted=0.
  allocate(RAefficiency_vt(nblomin,nent))
  RAefficiency_vt=0.

  allocate(xint1v(nemax,nveg))
  allocate(xint1s(nsol))
  allocate(xintav(nemax,nveg))
  allocate(xintas(nsol))

  allocate(Spar(nent,60))
  Spar=0.

  call DirectBeam_Interception(day, hour, truesolartime)

  if (hdeg.gt.2.) then      !MARC  pb with hdeg ->0 
   do iblo=1,nblomin
    if (glob(iblo).gt.0.) then
     call Spectral_Radiation_Balance(iblo)
    endif
   end do
  endif

 end subroutine swrb_doall


 subroutine sundirection(sunheight,sunazimuth,latitude,longitude,timezone,day,hour,truesolartime)

! Computation of the sun direction (i.e. height and azimuth, in degrees) from grid location and time
! From programs given by Grebet (1993, in Crop structure and light microclimate)
! Sun azimuth is computed with the South clockwise convention (East = -90, West = 90)
! ajout du flag truesolartime si hour est l'heure solaire (ajout mwoussen 23/03/2022)

  real :: sunheight, sunazimuth
  real :: latitude, longitude
  real :: timezone, day, hour
  logical :: truesolartime

  real :: om, teta, sidec, codec, tphi, dphi, eqntime
  real :: silat, colat, pi
  real :: TSThour, hour_angle, sinh, cosaz

  pi=2.*acos(0.)

  om =0.017202*(day-3.244)
  teta=om+0.03344*sin(om)*(1+0.021*cos(om))-1.3526
  tphi=0.91747*sin(teta)/cos(teta)
  dphi=ATAN(tphi)-om+1.3526
  if (dphi+1..le.0.) then
   dphi=amod(dphi+1+1000.*pi,pi)-1.
  end if
  eqntime=dphi*229.2 ! Equation of time (in min)

  sidec=0.3978*sin(teta) ! Sine and cosine of sun declination
  codec=cos(asin(sidec))

  silat=sin(latitude*pi/180.) ! Sine and cosine of latitude
  colat=cos(latitude*pi/180.)

  ! active ou non le calcul de l'heure solaire
  if(.NOT. truesolartime) then
    TSThour =amod(hour+timezone+longitude/15.-eqntime/60.,24.) ! True Solar Time
  else
    TSThour =hour
  endif

  hour_angle = (TSThour-12)*pi/12.
  sinh = silat*sidec + colat*codec*cos(hour_angle)
  sunheight=asin(sinh)
  cosaz= (silat*codec*cos(hour_angle)-colat*sidec)/cos(sunheight)
  sunazimuth=sign(acos(cosaz),hour_angle)

  sunheight=sunheight*180./pi  ! Conversion to degrees
  sunazimuth=sunazimuth*180./pi

  ! ajout mwoussen 21/02/2022 pour utiliser sundirection
  ! indépendamment de DirectBeam_Interception
  hdeg = sunheight
  azdeg = sunazimuth

 end subroutine sundirection


 subroutine DirectBeam_Interception(day,hour,truesolartime)

  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception

  real :: day, hour
  logical :: truesolartime

!  write(*,*) 'Computing interception of direct radiation ...'

  call sundirection(hdeg,azdeg,latitude,longitude,timezone,day,hour,truesolartime)
  

  azdeg=azdeg-orientation  ! azimuth with regard to 3Dgrid X-axis

!  Direct beam interception (includes computation of extinction coefficient, beam sampling, and exchange coefficients)

  if (hdeg.gt.5.) then      !MARC  pb with hdeg ->0 
   scattering=.FALSE.   ! only computation of incident direct radiation
   call di_doall(hdeg, azdeg, 0., dpx, dpy,scattering, isolated_box)  ! rem: sun angles in degrees
  else
   riv=0.  ! If hdeg < 5�, interception of direct radiation is assumed to be zero
   ris=0.
  endif

 end subroutine DirectBeam_Interception


 subroutine Spectral_Radiation_Balance(iblo)

  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo

  logical :: iarret

  real, allocatable :: xintbv(:,:), xintbs(:) ! Intercepted flux of radiation, after current iteration

  integer :: parclass


!  Local array allocation

  allocate(xintbv(nemax,nveg))
  allocate(xintbs(nsol))

!  Premiere interception : direct + diffus incidents
!
!  - Pour la vegetation:
  do k=1,nveg
  do je=1,nje(k)
   xint1v(je,k)= dsg(iblo) * rdiv(je,k)+(1.-dsg(iblo))* riv(k)*share(je,k)
   xintav(je,k)= xint1v(je,k)
  end do
  end do

!  - Pour le sol:
  do k=1,nsol
   xint1s(k)= dsg(iblo) * rdis(k) + (1.-dsg(iblo))* ris(k)
   xintas(k)=xint1s(k)
  end do

!  - Pour le ciel:
  xintac=0.


! Resolution du bilan radiatif du couvert:
!    - intercepte culture
!    - transmis au sol

  iarret=.FALSE.
  do while (.NOT.iarret)

   xintbv=0.
   xintbs=0.
   xintbc=0.

!   Flux intercepte par le ciel, i.e. reflected radiation : xintbc
   do ks=1,nveg
   do jes=1,nje(ks)
    xintbc=xintbc+2.*rf(nume(jes,ks),iblo)*ffcv(ks,jes)*xintav(jes,ks) ! Contribution of scattered radiation by vegetated voxels
   end do
   end do
   do ks=1,nsol
    xintbc=xintbc + rs(iblo)*ffcs(ks)*xintas(ks)  ! Contribution of scattered radiation by ground zones
   end do

!   Flux interceptes par la vegetation : xintbv
   do k=1,nveg
   do je=1,nje(k)
    do ks=1,nveg
    do jes=1,nje(ks)
     xintbv(je,k)=xintbv(je,k) + 2.*rf(nume(jes,ks),iblo)*ffvv(k,je,ks,jes)*xintav(jes,ks)  ! Contribution of scattered radiation by vegetated voxels
    end do
    end do
    do ks=1,nsol
     xintbv(je,k)=xintbv(je,k) + rs(iblo)*ffvs(k,je,ks)*xintas(ks) ! Contribution of scattered radiation by ground zones
    end do
            xintav(je,k)=xintbv(je,k)+xint1v(je,k)  ! Adding 1st interception fluxes
   end do
   end do

!   Flux interceptes par le sol : xintbs
   do k=1,nsol
    do ks=1,nveg
    do jes=1,nje(ks)
     xintbs(k)=xintbs(k) + 2.*rf(nume(jes,ks),iblo)*ffsv(k,ks,jes)*xintav(jes,ks) ! Contribution of scattered radiation by vegetated voxels
    end do
    end do
    xintas(k)=xintbs(k)+xint1s(k)  ! Adding 1st interception fluxes
   end do

   criter=abs(xintbc-xintac)
   if (criter.lt.0.0001*total_ground_area) iarret=.TRUE.
   !write(*,*) iarret,xintbc/total_ground_area
   xintac=xintbc

  end do ! while (.NOT.iarret)


!  Calculs sur les flux de base :

!  1- Rayonnements reflechi et transmis.

  RAreflected(iblo)=xintac/total_ground_area
  RAtransmitted(iblo)=0.
  do k=1,nsol
   RAtransmitted(iblo)=RAtransmitted(iblo)+xintas(k)
   xintbs(k)=(xintas(k)-(1.-dsg(iblo))*ris(k))/(dx*dy) ! Transmitted radiation to shaded area in ground zone k
  end do
  RAtransmitted(iblo)=RAtransmitted(iblo)/total_ground_area

!  2- Efficiences d'interception : for each vegetation type jent, jent=1,nent

  do jent=1,nent
   RAefficiency_vt(iblo,jent)=0.
  end do
  do k=1,nveg
  do je=1,nje(k)
   jent=nume(je,k)
   RAefficiency_vt(iblo,jent)=RAefficiency_vt(iblo,jent)+xintav(je,k)
  end do
  end do
  do jent=1,nent
   RAefficiency_vt(iblo,jent)=RAefficiency_vt(iblo,jent)/total_ground_area*(1.-2.*rf(jent,iblo))
   aaaa=RAefficiency_vt(iblo,jent)
  end do


!         ski: Rayonnement direct intercepte (W)
!         Eclomb: Rayonnement absorbe par unite de surface ombragee (W/m2)
!         Eclens: Rayonnement direct absorbe par unite de surface ensoleillee (W.m-2)
!         SWRA_detailed(0,je,k): Rayt solaire absorbe par unite de surface ombragee (W/m2)
!         SWRA_detailed(1,je,k): idem pour la surface ensoleillee

  do k=1,nveg
  do je=1,nje(k)
   jent=nume(je,k)
   ski= direct(iblo)*riv(k)*share(je,k)
   Eclomb= glob(iblo)*xintav(je,k)-ski
   Eclomb= Eclomb*(1.-2.*rf(jent,iblo))
   Eclens= Ski * (1.-2.*rf(jent,iblo))
   RA_detailed(iblo,0,je,k)= Eclomb/S_vt_vx(je,k)  ! Absorbed radiation W per m� leaf area, in band iblo
   RA_detailed(iblo,1,je,k)= RA_detailed(iblo,0,je,k) + Eclens/S_detailed(1,je,k)
   SWRA_detailed(0,je,k)=SWRA_detailed(0,je,k) + RA_detailed(iblo,0,je,k)  ! Absorbed radiation W per m� leaf area, summing up all wavebands
   SWRA_detailed(1,je,k)=SWRA_detailed(1,je,k) + RA_detailed(iblo,1,je,k)
   end do
  end do


!  write(*,*) 'PARirrad: PAR leaf irradiance (�mol m-2 s-1)'     
!  - utilise pour calcul de J (flux d'electrons)
!  - utilise pour conductance stomatique

  if (iblo.eq.1) then
   do k=1,nveg
   do je=1,nje(k)
    jent=nume(je,k)
    do joe=0,1
     !PARirrad(joe,je,k)=RA_detailed(1,joe,je,k)*2.02/0.48/(1.-2.*rf(jent,iblo))           !11/06/2012 A PRIORI ERREUR NE PAS DIVISER PAR 0.48 CAR iblo =1 EST DEJA DANS LE PAR !
     !PARirrad(joe,je,k)=RA_detailed(1,joe,je,k)*2.02/(1.-2.*rf(jent,iblo))               !23/05/2013 Erreur, le coefficient de conversion WattPAR -> micromol est 4.6, 
     PARirrad(joe,je,k)=RA_detailed(1,joe,je,k)*4.6/(1.-2.*rf(jent,iblo))
     parclass=int(PARirrad(joe,je,k)/50.)+1
     if (parclass.gt.50) then
      !write (*,*) k, nume(je,k), joe, glob(iblo), PARirrad(joe,je,k), RA_detailed(1,joe,je,k), rf(jent,iblo)
      !pause
     else
      Spar(nume(je,k),parclass)=Spar(nume(je,k),parclass)+S_detailed(joe,je,k)
     endif
    end do
   end do
   end do
  endif

!  Distribution of PAR leaf irradiance at canopy scale, for each vegetation type

!  if (iblo.eq.1) then
!   do k=1,nveg
!    do je=1,nje(k)
!     do joe=0,1
!      parclass=int(PARirrad(joe,je,k)/50)+1
!      if (parclass.gt.50) then
!       !write (*,*) k, nume(je,k), joe, PARirrad(joe,je,k), RA_detailed(1,joe,je,k)
!       pause
!      endif
!      Spar(nume(je,k),parclass)=Spar(nume(je,k),parclass)+S_detailed(joe,je,k)
!     end do
!    end do
!   end do
!  endif


  deallocate(xintbv)
  deallocate(xintbs)

 end subroutine Spectral_Radiation_Balance

 subroutine swrb_destroy

  if (allocated(RA_detailed)) deallocate(RA_detailed)
  if (allocated(SWRA_detailed)) deallocate(SWRA_detailed)
  if (allocated(PARirrad)) deallocate(PARirrad)

  if (allocated(RAreflected)) deallocate(RAreflected)
  if (allocated(RAtransmitted)) deallocate(RAtransmitted)
  if (allocated(RAefficiency_vt)) deallocate(RAefficiency_vt)

  if (allocated(xint1v)) deallocate(xint1v)
  if (allocated(xint1s)) deallocate(xint1s)
  if (allocated(xintav)) deallocate(xintav)
  if (allocated(xintas)) deallocate(xintas)

  if (allocated(Spar)) deallocate(Spar)


 end subroutine swrb_destroy

end module shortwave_balance


!------------------------------------------------------------------------------
