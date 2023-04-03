!------------------------------------------------------------------------------

module energy_balance

real, allocatable :: E_vt_vx(:,:)  ! Evaporation rate per voxel and vegetation type
real, allocatable :: E_vx(:)       ! Evaporation rate per voxel
real, allocatable :: E_vt(:)    ! Evaporation rate per vegetation type
real, allocatable :: E_ss_vt(:,:) ! Evaporation rate of shaded/sunlit area per vegetation type
real ::      E_ss(0:1)      ! Evaporation rate of canopy shaded/sunlit area
real ::      E_canopy         ! Evaporation rate of canopy
real ::      H_canopy         ! Sensible heat rate of canopy

real, allocatable :: ts(:,:,:)   ! Surface temperature of shaded/sunlit foliage of each vegetation type in each voxel 
real, allocatable :: ts_iter(:,:,:)  ! Surface temperature of shaded/sunlit foliage of each vegetation type in each voxel at iteration niter-1       
real, allocatable :: Sts(:,:)    ! Leaf area distribution per leaf temperature classes, for each vegetation type
real, allocatable :: gs(:,:,:)   ! Stomatal conductance (two sides) (m s-1) of shaded/sunlit are of each vegetation type in each voxel

real, allocatable :: rco2(:,:,:)  ! Total leaf resistance (2 sides, boundary layer + stomatal, s m-1) of each voxel for CO2 transport

real, allocatable :: E(:,:,:)   ! Latent heat flux by shaded/sunlit foliage of each vegetation type in each voxel

real, parameter, private :: xtoler_def = 1e-6, toler_def = 1e-6            !Brenqt method
integer, parameter, private :: maxiter_def = 100, printmod_def = -1        !Brenqt method

contains

 subroutine eb_doall_mine

! Computation of the energy balance of each vegetation type in each voxel.
!   - compute net radiation, transpiration
!   - computestomatal conductance, leaf resistances
!   - compute leaf temperature
!   - take into account possible mined leaves (Cf. S. Pincebourde's thesis)

  use constant_values
  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo
  use shortwave_balance



  real, allocatable  :: raco2(:)   ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport

  real, allocatable  :: omega_factor(:,:,:) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel



  real, allocatable :: rni(:,:,:)   ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  real, allocatable :: rayirt(:,:,:)  ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

  real :: rayirtsol, ratm

  logical :: next_iter      ! .TRUE. if an additional iteration is needed to solve the energy balance
  integer :: niter        ! Iteration #
  real  :: bilanmax       ! Maximum departure from energy balance observed during a given iteration

  real  :: ga, ra       ! leaf boundary layer conductance (m s-1) / resistance (s m-1)
  real  :: es, des       ! Saturating water vapor pressure (Pa), and its derivative with regard to leaf temperature

  real  :: rss, rsi, drsi     ! Stomatal resistance / conductance of upper (rss) and lower (rsi, gsi) sides, and some derivatives

  integer :: jent        ! Current vegetation type #
  real  :: leaf_nitrogen, par_irrad, leaf_temp, VPDair ! Input parameters for Jarvis stomatal model

  real  :: rv, drv, rh      ! Total resistance to water vapour (rv) and heat (rh) transfer, and derivative of rv
  real  :: rn, drn       ! Net radiation of current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: devap        ! Derivative of current latent heat flux (with regard to temperature)
  real  :: h, dh        ! Sensible heat flux from current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: hem, dhem      ! Heat exchange between mine and healthy tissue (W m-2), and its derivative
  real  :: bilan, dbilan     ! Departure from energy balance in current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative

  real  :: rssCO2, rsico2     ! Lower ans upper side stomatal resistance (s m-1) for CO2 transport

  real :: epsilon1          ! Intermediate term in decoupling factor calcultation

  integer :: tsclass
  
  call cv_set ! Setting physical constant values ...


!  Allocation of module arrays

  call eb_destroy

  allocate(E_vt_vx(nemax,nveg))
  allocate(E_vx(nveg))
  allocate(E_vt(nent))
  allocate(E_ss_vt(0:1,nent))
  allocate(E(0:1,nemax,nveg))

  allocate(ts(0:1,nemax,nveg))
  allocate(gs(0:1,nemax,nveg))
  allocate(rco2(0:1,nemax,nveg))

  allocate(Sts(nent,0:100))

!  Initialisation of output variables for energy balance:

  E_vt_vx = 0.  ! Evaporation rate per voxel and vegetation type
  E_vx = 0.       ! Evaporation rate per voxel
  E_vt = 0.    ! Evaporation rate per vegetation type
  E_ss_vt = 0. ! Evaporation rate of shaded/sunlit area per vegetation type
  E_ss = 0.      ! Evaporation rate of canopy shaded/sunlit area
  E_canopy = 0.      ! Evaporation rate of canopy
  H_canopy = 0.      ! Sensible heat rate of canopy
  E = 0.
  Sts=0.

!  Allocation of local arrays


  allocate(raco2(nveg))
  allocate(omega_factor(0:1,nemax,nveg))
  allocate(rni(0:1,nemax,nveg))
  allocate(rayirt(0:1,nemax,nveg))


!  Starting net radiation balance

  rayirtsol=sigma*(tsol+273.15)**4*dx*dy  ! TIR radiation emitted by each ground zone (W)
  do k=1,nveg
  do je=1,nje(k)
!   Contribution of atmospheric radiation to long wave radiation balance of type je in voxel k
         ratm=ratmos*rdiv(je,k)/S_vt_vx(je,k)
!   Contribution of TIR radiation emitted by ground zones ksol, ksol=1,nsol
   rsol=0.
   do ksol=1,nsol
    rsol=rsol+ffvs(k,je,ksol)
   end do
         rsol=rsol*rayirtsol/S_vt_vx(je,k)

         do joe=0,1
            rni(joe,je,k)=SWRA_detailed(joe,je,k)+ratm+rsol
   end do
  end do
  end do

!-----------------------------!
!  Starting energy balance !
!-----------------------------!

!
!  Initialisation of leaf temperature, i.e. equal to air temperature taref
!
  do k=1,nveg
  do je=1,nje(k)
  do joe=0,1
   ts(joe,je,k)=taref
         rayirt(joe,je,k)=2.*sigma*(taref+273.15)**4*S_detailed(joe,je,k)  ! TIR radiation flux emitted by shaded / sunlit vegetation in voxels (including 2 sides)
  end do
  end do
  end do

!
!  Iterative solving of energy balance for each vegetation type in each voxel
!

      niter=0
  next_iter=.TRUE.

  do while (next_iter)

   niter=niter+1
   !write(*,*) 'Iteration:',niter

   bilanmax=0.
   E_canopy=0. ! Pour essai Shuttleworth-Wallace (09 Dec 2002, avec FB)
   H_canopy=0.    ! idem

   do k=1,nveg     ! Computation of the energy balance

   do je=1,nje(k)    ! For each voxel, each vegetation type, shaded and sunlit area

   do joe=0,1
   !write(*,*) 'joe:',joe

    jent=nume(je,k)
    !write(*,*) 'jent:',jent
    leaf_nitrogen = N_detailed(je,k)
    par_irrad=PARirrad(joe,je,k)
    leaf_temp=ts(joe,je,k)
    esair=610.78*exp((17.27*taref)/(237.3+taref))
    VPDair=esair-earef
    !write(*,*) 'VPDair:',VPDair
!    Leaf boundary resistance / conductance
!
!    ra : one-side resistance, in s.m-1
!    ga : one-side conductance, in m s-1
    !write(*,*) 'numz(k)',numz(k)
    !write(*,*) 'uref(numz(k))',uref(numz(k))
    ga=Aga(jent,1)*uref(numz(k))+Aga(jent,2)

    !write(*,*) 'ga',ga
    ra=1./ga

!    Saturating water vapor pressure, es, at temperature ts: Tetens' formula (1930), en Pa
!    and its derivative des, with regard to temperature ts

    es=610.78*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))
    des=610.78*17.27*237.3/((237.3+ts(joe,je,k))**2)*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))


!    Stomatal resistance (in s m-1) / conductance (in m s-1)
!    rss:  upper side stomatal resistance
!    rsi:  lower side stomatal resistance
!    gs :  lower side stomatal conductance

    rss=10000.    ! Arbitrary high value
    !write(*,*) 'call Jarvis_stomata avant'
    call Jarvis_stomata(jent,leaf_nitrogen,par_irrad,caref,HRsol,leaf_temp,VPDair,ga,rsi,drsi)
    !write(*,*) 'call Jarvis_stomata apres'

!    Total resistances, i.e. boundary layer + stomatal and 2 sides, in s m-1
!    rv : water vapour transfert
!    rh : heat transfert

    if (es.lt.earef) then   ! Saturation at leaf surface (i.e. dew formation)
     rv=ra/2.
     drv=0.
     else
     rv=(rss+ra)*(rsi+ra)/(rss+rsi+2.*ra)
     drv=drsi*((rss+ra)/(rss+rsi+2*ra))**2
    endif

    rh=ra/2.

!
!    Computation of the energy terms of the energy balance
!    (as a function of leaf temperature)

!    1- Net radiation : rn (W m-2)

    rn=rni(joe,je,k)
    do ks=1,nveg    ! Contribution of emitted radiation by shaded / sunlit vegetation in every voxel
    do jes=1,nje(ks)
    do joes=0,1
     rn=rn+ffvv(k,je,ks,jes)*rayirt(joes,jes,ks)/S_vt_vx(je,k)
    end do
    end do
    end do
    rn=rn-rayirt(joe,je,k)/S_detailed(joe,je,k)

!    1'- Derivative of net radiation with regard to leaf temperature: drn

    drn=2*4*sigma*(ts(joe,je,k)+273.15)**3*(ffvv(k,je,k,je)*S_detailed(joe,je,k)/(S_vt_vx(je,k))-1.)


!    2- Latent heat flux: evap, in W m-2

    E(joe,je,k)=(rho*cp/gamma)*(es-earef)/rv
    E_canopy=E_canopy+E(joe,je,k)*S_detailed(joe,je,k)

!    2'- Derivative of latent heat flux with regard to leaf temperature: devap

    devap=(rho*cp/gamma)*(des*rv-(es-earef)*drv)/rv**2


!    3- Sensible heat flux: h (W m-2)

    h=(rho*cp)*(ts(joe,je,k)-taref)/rh
    H_canopy=H_canopy+h*S_detailed(joe,je,k)

!    3'- Derivative of sensible heat flux with regard to leaf temperature: dh

    dh=rho*cp/rh

!    4-  Heat exchange between the mine and healthy tissue : Cf. Thèse S. Pincebourde

    hem= float(ismine(jent))*(rho*cp)*(ts(joe,je,k)-ts(joe,1,k))*&
     &(0.05*(22.4/1000.)*(abs(ts(joe,je,k)-ts(joe,1,k))/epm(jent))**0.25)*0.13

!    rem: This assumes that healthy tissue is vegetation type #1.

!    4'- Derivative of heat exchange between the mine and healthy tissue

!    dhem= float(ismine(jent))*(rho*cp)*(0.05*(1000./22.4)/(epm(jent))**(0.25))*1.25*abs(ts(joe,je,k)-ts(joe,1,k))**0.25*0.13
    if (abs(hem).lt.1.e-5) then
     dhem=0.
    else
     dhem=float(ismine(jent))*(rho*cp)*(0.05*(22.4/1000.)/&
     &(epm(jent))**(0.25))*(abs(ts(joe,je,k)-ts(joe,1,k))&
     &**0.25+0.25*(ts(joe,je,k)-ts(joe,1,k))/abs(ts(joe,je,k)&
     &-ts(joe,1,k))**0.75)*0.13
    endif

!    5- Energy balance (bilan) and its derivative (dbilan)

    bilan=rn-E(joe,je,k)-h-hem
    dbilan=drn-devap-dh-dhem
    bilanmax=amax1(bilanmax,abs(bilan))

!    6- Updating leaf temperature (and emitted TIR radiation) for next iteration

    ts(joe,je,k)=ts(joe,je,k)-(bilan/dbilan)
    rayirt(joe,je,k)=2.*sigma*(ts(joe,je,k)+273.15)**4*S_detailed(joe,je,k)


!    Computation of resistances to CO2 transport (in s m-1)
!
    raco2(k)=1.37*ra    ! Leaf boundary layer resistance for CO2 transfert
    rssco2=1.6*rss     ! Upper side stomatal resistance for CO2 transfert
    rsico2=1.6*rsi     ! Lower side stomatal resistance for CO2 transfert
!    Total resistance to CO2 transfert, i.e. leaf boundary layer + stomatal and 2 sides
    rco2(joe,je,k)=(rssco2+raco2(k))*(rsico2+raco2(k))/(rssco2+rsico2+2.*raco2(k))
!    Conversion to µmol CO2-1 m2 s   (a 25 °C)
    rco2(joe,je,k)=rco2(joe,je,k)/1000./0.0414 / 1.e6


!    Computation of the decoupling factor (omega), Jarvis et Mc Naughton (1986)
!
    gs(joe,je,k)=1/rss + 1/rsi
    epsilon1=des/gamma + 2.
    omega_factor(joe,je,k)=epsilon1/(epsilon1 + 2. * ga/gs(joe,je,k) )

   end do    ! Loop-end of computation of the energy balance
   end do
   end do

   !write(*,*) 'Iteration #',niter,'Maximum deviation from energy balance (W m-2): ',bilanmax

   next_iter = (bilanmax.gt.1).and.(niter.lt.100)

  end do

!  Summing up evaporation rates at different levels

  do k=1,nveg
   do je=1,nje(k)
    jent=nume(je,k)
    do joe=0,1
     E(joe,je,k) = E(joe,je,k) * S_detailed(joe,je,k)/lambda/18*1000.  ! Evaporation rate in mmol H20 s-1
     E_vt_vx(je,k) = E_vt_vx(je,k) + E(joe,je,k)
     E_vx(k) = E_vx(k) + E(joe,je,k)
     E_vt(jent) = E_vt(jent) + E(joe,je,k)
     E_ss_vt(joe,jent) = E_ss_vt(joe,jent) + E(joe,je,k)
     E_ss(joe) = E_ss(joe) + E(joe,je,k)
    end do
   end do
  end do
  E_canopy = E_canopy / lambda/18*1000.  ! Evaporation rate in mmol H20 s-1


!  Normalisation of Es by leaf area

  do k=1,nveg
   do je=1,nje(k)
    E_vt_vx(je,k)=E_vt_vx(je,k)/S_vt_vx(je,k)
   end do
   E_vx(k)=E_vx(k)/S_vx(k)
  end do
  do jent=1,nent
   do joe=0,1
    E_ss_vt(joe,jent)=E_ss_vt(joe,jent)/S_ss_vt(joe,jent)
   end do
   E_vt(jent)=E_vt(jent)/S_vt(jent)
  end do
  do joe=0,1
   E_ss(joe)=E_ss(joe)/S_ss(joe)
  end do
  E_canopy = E_canopy / S_canopy       ! Evaporation rate in mmol H20 s-1 m-2
  H_canopy = H_canopy / S_canopy        


!  Distribution of leaf temperature at canopy scale

  do k=1,nveg
   do je=1,nje(k)
    do joe=0,1
     tsclass=int(ts(joe,je,k))+1
     Sts(nume(je,k),tsclass)=Sts(nume(je,k),tsclass)+S_detailed(joe,je,k)
    end do
   end do
  end do



!  write(*,*) 'gs',gs(0,1,kxyz(4,9,8)),gs(1,1,kxyz(4,9,8))
!  write(*,*) 'rni',rni(0,1,kxyz(4,9,8)),rni(1,1,kxyz(4,9,8))


! Deallocation of local arrays used in subroutine eb_doall

  deallocate(raco2)    ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport
!  deallocate(gs)     ! Stomatal conductance (two sides) (m s-1) of shaded/sunlit are of each vegetation type in each voxel
  deallocate(omega_factor) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel
  deallocate(rni)    ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(rayirt)   ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

 end subroutine eb_doall_mine
!-----------------------------------------------------------eb_doall-------------------------------------------------------------
 subroutine eb_doall

! Computation of the energy balance of each vegetation type in each voxel.
!   - compute net radiation, transpiration
!   - computestomatal conductance, leaf resistances
!   - compute leaf temperature


  use constant_values
  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo
  use shortwave_balance



  real, allocatable  :: raco2(:)   ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport

  real, allocatable  :: omega_factor(:,:,:) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel



  real, allocatable :: rni(:,:,:)   ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  real, allocatable :: rayirt(:,:,:)  ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

  real :: rayirtsol, ratm

  logical :: next_iter      ! .TRUE. if an additional iteration is needed to solve the energy balance
  integer :: niter        ! Iteration #
  real  :: bilanmax       ! Maximum departure from energy balance observed during a given iteration

  real  :: ga, ra       ! leaf boundary layer conductance (m s-1) / resistance (s m-1)
  real  :: es, des       ! Saturating water vapor pressure (Pa), and its derivative with regard to leaf temperature

  real  :: rss, rsi, drsi     ! Stomatal resistance / conductance of upper (rss) and lower (rsi, gsi) sides, and some derivatives

  integer :: jent        ! Current vegetation type #
  real  :: leaf_nitrogen, par_irrad, leaf_temp, VPDair ! Input parameters for Jarvis stomatal model

  real  :: rv, drv, rh      ! Total resistance to water vapour (rv) and heat (rh) transfer, and derivative of rv
  real  :: rn, drn       ! Net radiation of current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: devap        ! Derivative of current latent heat flux (with regard to temperature)
  real  :: h, dh        ! Sensible heat flux from current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: bilan, dbilan     ! Departure from energy balance in current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative

  real  :: rssCO2, rsico2     ! Lower ans upper side stomatal resistance (s m-1) for CO2 transport

  real :: epsilon1          ! Intermediate term in decoupling factor calcultation
  
  integer :: tsclass

  call cv_set ! Setting physical constant values ...


!  Allocation of module arrays

  call eb_destroy

  allocate(E_vt_vx(nemax,nveg))
  allocate(E_vx(nveg))
  allocate(E_vt(nent))
  allocate(E_ss_vt(0:1,nent))
  allocate(E(0:1,nemax,nveg))
  allocate(ts(0:1,nemax,nveg))
  allocate(gs(0:1,nemax,nveg))
  allocate(rco2(0:1,nemax,nveg))

!  allocate(Sts(nent,0:100))

!  Initialisation of output variables for energy balance:

  E_vt_vx = 0.  ! Evaporation rate per voxel and vegetation type
  E_vx = 0.       ! Evaporation rate per voxel
  E_vt = 0.    ! Evaporation rate per vegetation type
  E_ss_vt = 0. ! Evaporation rate of shaded/sunlit area per vegetation type
  E_ss = 0.      ! Evaporation rate of canopy shaded/sunlit area
  E_canopy = 0.      ! Evaporation rate of canopy
  H_canopy = 0.      ! Sensible heat rate of canopy
  E = 0.
!  Sts=0.
!  write(*,*) 'fin init output'
!  Allocation of local arrays


  allocate(raco2(nveg))
  allocate(omega_factor(0:1,nemax,nveg))
  allocate(rni(0:1,nemax,nveg))
  allocate(rayirt(0:1,nemax,nveg))


!  Starting net radiation balance

  rayirtsol=sigma*(tsol+273.15)**4*dx*dy  ! TIR radiation emitted by each ground zone (W)
  do k=1,nveg
  do je=1,nje(k)
!   Contribution of atmospheric radiation to long wave radiation balance of type je in voxel k
         ratm=ratmos*rdiv(je,k)/S_vt_vx(je,k)
!   Contribution of TIR radiation emitted by ground zones ksol, ksol=1,nsol
   rsol=0.
   do ksol=1,nsol
    rsol=rsol+ffvs(k,je,ksol)
   end do
         rsol=rsol*rayirtsol/S_vt_vx(je,k)

         do joe=0,1
            rni(joe,je,k)=SWRA_detailed(joe,je,k)+ratm+rsol
   end do
  end do
  end do
!  write(*,*) 'fin Rn balance'
!-----------------------------!
!  Starting energy balance !
!-----------------------------!

!
!  Initialisation of leaf temperature, i.e. equal to air temperature taref
!
!  write(*,*) 'Init TLeaf and RayIRT ...'
  do k=1,nveg
  do je=1,nje(k)
  do joe=0,1
   if (joe.eq.0) then
     ts(joe,je,k)=taref
   else
     ts(joe,je,k)=taref
   end if
   rayirt(joe,je,k)=2.*sigma*(taref+273.15)**4*S_detailed(joe,je,k)  ! TIR radiation flux emitted by shaded / sunlit vegetation in voxels (including 2 sides)
   !write (*,*) 'k, je, joe, RayIRT1, TempLeaf =', k,je,joe,rayirt(joe,je,k),ts(joe,je,k)
  end do
  end do
  end do
!  write(*,*) '.........................'
!
!  Iterative solving of energy balance for each vegetation type in each voxel
!

  niter=0
  next_iter=.TRUE.

  do while (next_iter)

   niter=niter+1
!   write(*,*) 'Iteration solve:'!,niter

   bilanmax=0.
   E_canopy=0. ! Pour essai Shuttleworth-Wallace (09 Dec 2002, avec FB)
   H_canopy=0.    ! idem

   do k=1,nveg     ! Computation of the energy balance

   do je=1,nje(k)    ! For each voxel, each vegetation type, shaded and sunlit area

   do joe=0,1
!   write(*,*) 'joe:',joe        
    jent=nume(je,k)
!    write(*,*) 'jent:',jent
    leaf_nitrogen = N_detailed(je,k)
    par_irrad=PARirrad(joe,je,k)
    leaf_temp=ts(joe,je,k)   
    esair=610.78*exp((17.27*taref)/(237.3+taref))
    VPDair=esair-earef
!    write(*,*) 'VPDair:',VPDair
!    Leaf boundary resistance / conductance
!
!    ra : one-side resistance, in s.m-1
!    ga : one-side conductance, in m s-1
    !write(*,*) 'numz(k)',numz(k)
    !write(*,*) 'uref(numz(k))',uref(numz(k))
    ga=Aga(jent,1)*uref(numz(k))+Aga(jent,2)

 !   write(*,*) 'ga',ga
    ra=1./ga

!    Saturating water vapor pressure, es, at temperature ts: Tetens' formula (1930), en Pa
!    and its derivative des, with regard to temperature ts

    es=610.78*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))
    des=610.78*17.27*237.3/((237.3+ts(joe,je,k))**2)*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))


!    Stomatal resistance (in s m-1) / conductance (in m s-1)
!    rss:  upper side stomatal resistance
!    rsi:  lower side stomatal resistance
!    gs :  lower side stomatal conductance

    rss=10000.    ! Arbitrary high value
    !write(*,*) 'call Jarvis_stomata avant'
    call Jarvis_stomata(jent,leaf_nitrogen,par_irrad,caref,HRsol,leaf_temp,VPDair,ga,rsi,drsi)
    !write(*,*) 'call Jarvis_stomata apres'

!    Total resistances, i.e. boundary layer + stomatal and 2 sides, in s m-1
!    rv : water vapour transfert
!    rh : heat transfert

    if (es.lt.earef) then   ! Saturation at leaf surface (i.e. dew formation)
     rv=ra/2.
     drv=0.
    else
     rv=(rss+ra)*(rsi+ra)/(rss+rsi+2.*ra)
     drv=drsi*((rss+ra)/(rss+rsi+2*ra))**2
    endif

    rh=ra/2.
    !write (*,*) niter,next_iter,k,je,joe,rsi,rv,leaf_temp
!
!    Computation of the energy terms of the energy balance
!    (as a function of leaf temperature)

!    1- Net radiation : rn (W m-2)

    rn=rni(joe,je,k)
    do ks=1,nveg    ! Contribution of emitted radiation by shaded / sunlit vegetation in every voxel
    do jes=1,nje(ks)
    do joes=0,1
     rn=rn+ffvv(k,je,ks,jes)*rayirt(joes,jes,ks)/S_vt_vx(je,k)
    end do
    end do
    end do
    rn=rn-rayirt(joe,je,k)/S_detailed(joe,je,k)
!    write(*,*) 'Rn',rn

!    1'- Derivative of net radiation with regard to leaf temperature: drn

    drn=2*4*sigma*(ts(joe,je,k)+273.15)**3*(ffvv(k,je,k,je)*S_detailed(joe,je,k)/(S_vt_vx(je,k))-1.)


!    2- Latent heat flux: evap, in W m-2

    E(joe,je,k)=(rho*cp/gamma)*(es-earef)/rv
    E_canopy=E_canopy+E(joe,je,k)*S_detailed(joe,je,k)

!    2'- Derivative of latent heat flux with regard to leaf temperature: devap

    devap=(rho*cp/gamma)*(des*rv-(es-earef)*drv)/rv**2


!    3- Sensible heat flux: h (W m-2)

    h=(rho*cp)*(ts(joe,je,k)-taref)/rh
    H_canopy=H_canopy+h*S_detailed(joe,je,k)

!    3'- Derivative of sensible heat flux with regard to leaf temperature: dh

    dh=rho*cp/rh

!    5- Energy balance (bilan) and its derivative (dbilan)

    bilan=rn-E(joe,je,k)-h
!    write(*,*) 'Iteration #',niter,', voxel', k,', joe,',joe,' temp,',ts(joe,je,k),&
!    &' rn, rayirt, E(joe,je,k), h en (W m-2): ',rn, rayirt(joe,je,k)/S_detailed(joe,je,k), E(joe,je,k), h
    
    dbilan=drn-devap-dh
    bilanmax=amax1(bilanmax,abs(bilan))

!    6- Updating leaf temperature (and emitted TIR radiation) for next iteration
    
    ts(joe,je,k)=ts(joe,je,k)-(bilan/dbilan)
    rayirt(joe,je,k)=2.*sigma*(ts(joe,je,k)+273.15)**4*S_detailed(joe,je,k)


!    Computation of resistances to CO2 transport (in s m-1)
!
    raco2(k)=1.37*ra    ! Leaf boundary layer resistance for CO2 transfert
    rssco2=1.6*rss     ! Upper side stomatal resistance for CO2 transfert
    rsico2=1.6*rsi     ! Lower side stomatal resistance for CO2 transfert
!    Total resistance to CO2 transfert, i.e. leaf boundary layer + stomatal and 2 sides
    rco2(joe,je,k)=(rssco2+raco2(k))*(rsico2+raco2(k))/(rssco2+rsico2+2.*raco2(k))
!    Conversion to µmol CO2-1 m2 s   (a 25 °C)
    rco2(joe,je,k)=rco2(joe,je,k)/1000./0.0414 / 1.e6

!    Computation of the decoupling factor (omega), Jarvis et Mc Naughton (1986)
!
    gs(joe,je,k)=1/rss + 1/rsi
    epsilon1=des/gamma + 2.
    omega_factor(joe,je,k)=epsilon1/(epsilon1 + 2. * ga/gs(joe,je,k) )
    
!   write(*,*) 'Iteration #',niter,',  joe, Tleaf: ',joe, ts(joe,je,k)

   end do    ! Loop-end of computation of the energy balance
   end do
   end do
 
   
   write(*,*) 'Iteration #',niter,'Maximum deviation from energy balance (W m-2): ',bilanmax

   next_iter = (bilanmax.gt.(0.1)).and.(niter.lt.200)
   !next_iter = (niter.lt.1)

  end do
 

!   write(*,*) 'Iteration #',niter,'Maximum deviation from energy balance (W m-2): ',bilanmax 
  
  !write(*,*) 'niter,next_iter,k,je,joe,uref(numz(k)),rh,rn,E(joe,je,k),h'
  !do k=1,nveg     ! Computation of the energy balance
  ! do je=1,nje(k)    ! For each voxel, each vegetation type, shaded and sunlit area
  !   do joe=0,1 
  !      write(*,*) niter,next_iter,k,je,joe,uref(numz(k)),rh,rn,E(joe,je,k),h
  !   end do
  ! end do
  !end do
 ! write(*,*) 'E_canopy =', E_canopy
 ! Summing up evaporation rates at different levels

  do k=1,nveg
   do je=1,nje(k)
    jent=nume(je,k)
    do joe=0,1
     E(joe,je,k) = E(joe,je,k) * S_detailed(joe,je,k)/lambda/18*1000.  ! Evaporation rate in mmol H20 s-1
     E_vt_vx(je,k) = E_vt_vx(je,k) + E(joe,je,k)
     E_vx(k) = E_vx(k) + E(joe,je,k)
     E_vt(jent) = E_vt(jent) + E(joe,je,k)
     E_ss_vt(joe,jent) = E_ss_vt(joe,jent) + E(joe,je,k)
     E_ss(joe) = E_ss(joe) + E(joe,je,k)
    end do      
   ! write(*,*) 'k, je, Evap = ', k, je, E(0,je,k), E(1,je,k)
   end do
  end do
  E_canopy = E_canopy / lambda/18*1000.  ! Evaporation rate in mmol H20 s-1


!  Normalisation of Es by leaf area

  do k=1,nveg
   do je=1,nje(k)
    E_vt_vx(je,k)=E_vt_vx(je,k)/S_vt_vx(je,k)
   end do
   E_vx(k)=E_vx(k)/S_vx(k)
  end do
  do jent=1,nent
   do joe=0,1
    E_ss_vt(joe,jent)=E_ss_vt(joe,jent)/S_ss_vt(joe,jent)
   end do
   E_vt(jent)=E_vt(jent)/S_vt(jent)
  end do
  do joe=0,1
   E_ss(joe)=E_ss(joe)/S_ss(joe)
  end do
  E_canopy = E_canopy / S_canopy
  H_canopy = H_canopy / S_canopy


!  Distribution of leaf temperature at canopy scale

!  do k=1,nveg
!   do je=1,nje(k)
!    do joe=0,1
!     tsclass=int(ts(joe,je,k))+1
!     Sts(nume(je,k),tsclass)=Sts(nume(je,k),tsclass)+S_detailed(joe,je,k)
!    end do
!   end do
!  end do



! Deallocation of local arrays used in subroutine eb_doall
  !deallocate(E)     ! Latent heat flux by shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(raco2)    ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport
!  deallocate(gs)     ! Stomatal conductance (two sides) (m s-1) of shaded/sunlit are of each vegetation type in each voxel
  deallocate(omega_factor) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel
  deallocate(rni)    ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(rayirt)   ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

 end subroutine eb_doall
!------------------------------------------------------------------end  eb_doall

!-----------------------------------------------------------eb_doall2-
 subroutine eb_doall2

! Computation of the energy balance of each vegetation type in each voxel.
!   - compute net radiation, transpiration
!   - computestomatal conductance, leaf resistances
!   - compute leaf temperature


  use constant_values
  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo
  use shortwave_balance



  real, allocatable  :: raco2(:)   ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport

  real, allocatable  :: omega_factor(:,:,:) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel



  real, allocatable :: rni(:,:,:)   ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  real, allocatable :: rayirt(:,:,:)  ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

  real :: rayirtsol, ratm

  logical :: next_iter      ! .TRUE. if an additional iteration is needed to solve the energy balance
  integer :: niter        ! Iteration #
  real  :: bilanmax       ! Maximum departure from energy balance observed during a given iteration
  real ::  LeafDiffTempMax ! Maximum departure between two leaftemperature between two iterations   

  real  :: ga, ra       ! leaf boundary layer conductance (m s-1) / resistance (s m-1)
  real  :: es, des       ! Saturating water vapor pressure (Pa), and its derivative with regard to leaf temperature

  real  :: rss, rsi, drsi     ! Stomatal resistance / conductance of upper (rss) and lower (rsi, gsi) sides, and some derivatives

  integer :: jent        ! Current vegetation type #
  real  :: leaf_nitrogen, par_irrad, leaf_temp, VPDair ! Input parameters for Jarvis stomatal model

  real  :: rv, drv, rh      ! Total resistance to water vapour (rv) and heat (rh) transfer, and derivative of rv
  real  :: rn, drn       ! Net radiation of current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: devap        ! Derivative of current latent heat flux (with regard to temperature)
  real  :: h, dh        ! Sensible heat flux from current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: bilan, dbilan     ! Departure from energy balance in current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative

  real  :: rssCO2, rsico2     ! Lower ans upper side stomatal resistance (s m-1) for CO2 transport

  real :: epsilon1          ! Intermediate term in decoupling factor calcultation
  real :: xstar
  
  integer :: tsclass

  call cv_set ! Setting physical constant values ...


!  Allocation of module arrays

  call eb_destroy

  allocate(E_vt_vx(nemax,nveg))
  allocate(E_vx(nveg))
  allocate(E_vt(nent))
  allocate(E_ss_vt(0:1,nent))
  allocate(E(0:1,nemax,nveg))
  allocate(ts(0:1,nemax,nveg)) 
  allocate(ts_iter(0:1,nemax,nveg))
  allocate(gs(0:1,nemax,nveg))
  allocate(rco2(0:1,nemax,nveg))

!  allocate(Sts(nent,0:100))

!  Initialisation of output variables for energy balance:

  E_vt_vx = 0.  ! Evaporation rate per voxel and vegetation type
  E_vx = 0.       ! Evaporation rate per voxel
  E_vt = 0.    ! Evaporation rate per vegetation type
  E_ss_vt = 0. ! Evaporation rate of shaded/sunlit area per vegetation type
  E_ss = 0.      ! Evaporation rate of canopy shaded/sunlit area
  E_canopy = 0.      ! Evaporation rate of canopy
  H_canopy = 0.      ! Sensible heat rate of canopy
  E = 0.
!  Sts=0.
!  write(*,*) 'fin init output'
!  Allocation of local arrays


  allocate(raco2(nveg))
  allocate(omega_factor(0:1,nemax,nveg))
  allocate(rni(0:1,nemax,nveg))
  allocate(rayirt(0:1,nemax,nveg))


!  Starting net radiation balance

  rayirtsol=sigma*(tsol+273.15)**4*dx*dy  ! TIR radiation emitted by each ground zone (W)
  do k=1,nveg
   do je=1,nje(k)
!   Contribution of atmospheric radiation to long wave radiation balance of type je in voxel k
    ratm=ratmos*rdiv(je,k)/S_vt_vx(je,k)
!   Contribution of TIR radiation emitted by ground zones ksol, ksol=1,nsol
    rsol=0.
    do ksol=1,nsol
      rsol=rsol+ffvs(k,je,ksol)
    end do
    rsol=rsol*rayirtsol/S_vt_vx(je,k)
    do joe=0,1
      rni(joe,je,k)=SWRA_detailed(joe,je,k)+ratm+rsol
    end do
   end do
  end do
!  write(*,*) 'fin Rn balance'
!-----------------------------!
!  Starting energy balance !
!---

!
!  Initialisation of leaf temperature, i.e. equal to air temperature taref
!
!  write(*,*) 'Init TLeaf and RayIRT ...'
  do k=1,nveg
  do je=1,nje(k)
  do joe=0,1
     ts(joe,je,k)=taref
     ts_iter(joe,je,k)=taref
     !rayirt(joe,je,k)=2.*sigma*(taref+273.15)**4*S_detailed(joe,je,k)  ! TIR radiation flux emitted by shaded / sunlit vegetation in voxels (including 2 sides)  
   !write (*,*) 'k, je, joe, RayIRT, TempLeaf =', k,je,joe,rayirt(joe,je,k),ts(joe,je,k)
  end do
  end do
  end do
!  write(*,*) '.........................'
!
!  Iterative solving of energy balance for each vegetation type in each voxel
!
  niter=0
  next_iter=.TRUE.

  do while (next_iter)
   niter=niter+1
   bilanmax=0.   
   LeafDiffTempMax = 0.0
   E_canopy=0. ! Pour essai Shuttleworth-Wallace (09 Dec 2002, avec FB)
   H_canopy=0.    ! idem

   do k=1,nveg     ! Computation of the energy balance

   do je=1,nje(k)    ! For each voxel, each vegetation type, shaded and sunlit area

   do joe=0,1      
    leaf_temp=ts(joe,je,k) 
   !Rayo IR
    rayirt(joe,je,k) = RayoIR(sigma,leaf_temp)
    
   !Evaporation
   
    !write(*,*) 'k,je,joe:',k,je,joe
    jent=nume(je,k)
    leaf_nitrogen = N_detailed(je,k)
    par_irrad=PARirrad(joe,je,k)  
    esair=610.78*exp((17.27*taref)/(237.3+taref))
    VPDair=esair-earef
!    write(*,*) 'VPDair:',VPDair
!    Leaf boundary resistance / conductance
!
!    ra : one-side resistance, in s.m-1
!    ga : one-side conductance, in m s-1
    !write(*,*) 'numz(k)',numz(k)
    !write(*,*) 'uref(numz(k))',uref(numz(k))
    ga=Aga(jent,1)*uref(numz(k))+Aga(jent,2)
    ra=1.0/ga
 !   write(*,*) 'ga',ga


    !    Saturating water vapor pressure, es, at temperature ts: Tetens' formula (1930), en Pa
    !    and its derivative des, with regard to temperature ts
    !!es=610.78*exp((17.27*leaf_temp)/(237.3+leaf_temp))
  
    !    Stomatal resistance (in s m-1) / conductance (in m s-1)
    !    rss:  upper side stomatal resistance
    !    rsi:  lower side stomatal resistance
    !    gs :  lower side stomatal conductance

    rss=10000.    ! Arbitrary high value
    !write(*,*) 'call Jarvis_stomata avant'
    !!call Jarvis_stomata(jent,leaf_nitrogen,par_irrad,caref,HRsol,leaf_temp,VPDair,ga,rsi,drsi)
    !write(*,*) 'call Jarvis_stomata apres'

    !    Total resistances, i.e. boundary layer + stomatal and 2 sides, in s m-1
    !    rv : water vapour transfert
    !    rh : heat transfert

   !! if (es.lt.earef) then   ! Saturation at leaf surface (i.e. dew formation)
   !!  rv=ra/2.
   !! else
   !!  rv=(rss+ra)*(rsi+ra)/(rss+rsi+2.*ra)
   !! endif
    !    2- Latent heat flux: evap, in W m-2
  !!  E(joe,je,k)=(rho*cp/gamma)*(es-earef)/rv
    !!E_canopy=E_canopy+E(joe,je,k)*S_detailed(joe,je,k)
!
!    Computation of the energy terms of the energy balance
!    (as a function of leaf temperature)

!    1- Net radiation : rn (W m-2)

    rn=rni(joe,je,k)
    do ks=1,nveg    ! Contribution of emitted radiation by shaded / sunlit vegetation in every voxel
    do jes=1,nje(ks)
    do joes=0,1
     rn=rn+ffvv(k,je,ks,jes)*rayirt(joes,jes,ks)*S_detailed(joes,jes,ks)/S_vt_vx(je,k)
    end do
    end do
    end do
!    rn=rn-rayirt(joe,je,k)/S_detailed(joe,je,k)


 
!    3- Sensible heat flux: h (W m-2)   

    rh=ra/2.

    
!!TEST Brenqt
    
    call sub_brent(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,leaf_nitrogen,par_irrad,caref,&
    &HRsol,VPDair,xstar,EnergBilan,-90.0,150.0,xtoler_in=2.0*epsilon(0.0),printmod_in=0)
!    write(*,*) 'f(',xstar,')=',EnergBilan(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,&
!    &leaf_nitrogen,par_irrad,caref,HRsol,VPDair,xstar)
!    6- Updating leaf temperature (and emitted TIR radiation) for next iteration
    
    ts(joe,je,k)=xstar
    rayirt(joe,je,k)=RayoIR(sigma,ts(joe,je,k))
    
    
    bilan = EnergBilan(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,&
    &leaf_nitrogen,par_irrad,caref,HRsol,VPDair,xstar)
    
    bilanmax=amax1(bilanmax,abs(bilan))
    LeafDiffTempMax=amax1(LeafDiffTempMax,abs(ts_iter(joe,je,k)-ts(joe,je,k)))
     
    h=Convection(rho,cp,taref,rh,ts(joe,je,k))
    H_canopy=H_canopy+h*S_detailed(joe,je,k)

!    Computation of resistances to CO2 transport (in s m-1)
!   

    E(joe,je,k)=Evapotranspi(rho*cp/gamma,ga,jent,earef,leaf_nitrogen,&
    &par_irrad,caref,HRsol,VPDair,ts(joe,je,k))
    E_canopy=E_canopy+E(joe,je,k)*S_detailed(joe,je,k)
    
!    write(*,*) 'Iteration #',niter,', voxel', k,', joe,',joe,' temp,',ts(joe,je,k),&
!    &' rn, rayirt, E(joe,je,k), h en (W m-2): ',rn-rayirt(joe,je,k),rayirt(joe,je,k), E(joe,je,k), h
        
    call Jarvis_stomata(jent,leaf_nitrogen,par_irrad,caref,HRsol,ts(joe,je,k),VPDair,ga,rsi,drsi)

    
    raco2(k)=1.37*ra    ! Leaf boundary layer resistance for CO2 transfert
    rssco2=1.6*rss     ! Upper side stomatal resistance for CO2 transfert
    rsico2=1.6*rsi     ! Lower side stomatal resistance for CO2 transfert
!    Total resistance to CO2 transfert, i.e. leaf boundary layer + stomatal and 2 sides
    rco2(joe,je,k)=(rssco2+raco2(k))*(rsico2+raco2(k))/(rssco2+rsico2+2.*raco2(k))
!    Conversion to µmol CO2-1 m2 s   (a 25 °C)
    rco2(joe,je,k)=rco2(joe,je,k)/1000./0.0414/1.e6

!    Computation of the decoupling factor (omega), Jarvis et Mc Naughton (1986)
!
    !Marc Modif 17/05/2018
    es=610.78*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))
    if (es.lt.earef) then   ! Saturation at leaf surface (i.e. dew formation)
     rv=ra/2.
    else
     rv=(rss+ra)*(rsi+ra)/(rss+rsi+2.*ra)
    endif  
    gs(joe,je,k)=1/rss + 1/rsi
    epsilon1=des/gamma + 2.
    omega_factor(joe,je,k)=epsilon1/(epsilon1 + 2. * ga/gs(joe,je,k) )
!    write(*,*)  'rsi, rss =', rsi, rss
  
   !update ts_iter values for the next iteration
   ts_iter(joe,je,k)=ts(joe,je,k)
   
   end do    ! Loop-end of computation of the energy balance
   end do
   end do

   
   write(*,*) 'Iteration #',niter,'Maximum deviation from energy balance (W m-2) : ',bilanmax
   write(*,*) 'Iteration #',niter,'Maximum deviation of leaf temperature between two iter steps (C): ',LeafDiffTempMax
   next_iter = (LeafDiffTempMax.gt.(0.01)).and.(niter.lt.90)
   if (niter.eq.90) then
       write(*,*) 'WARNING ... the maximum number of iterations has been reached'
       write(*,*) 'WARNING ... Check the convergence of the iteration process'
       
   end if
    !next_iter = (niter.lt.50)
  end do
 
  
  !write(*,*) 'niter,next_iter,k,je,joe,uref(numz(k)),rh,rn,E(joe,je,k),h'
  !o k=1,nveg     ! Computation of the energy balance
  !do je=1,nje(k)    ! For each voxel, each vegetation type, shaded and sunlit area
  !   do joe=0,1 
  !      write(*,*) niter,next_iter,k,je,joe,uref(numz(k)),rh,rn,E(joe,je,k),h
  !   end do
  ! end do
  !end do
 ! write(*,*) 'E_canopy =', E_canopy
 ! Summing up evaporation rates at different levels

  do k=1,nveg
   do je=1,nje(k)
    jent=nume(je,k)
    do joe=0,1
     E(joe,je,k) = E(joe,je,k) * S_detailed(joe,je,k)/lambda/18*1000.  ! Evaporation rate in mmol H20 s-1
     E_vt_vx(je,k) = E_vt_vx(je,k) + E(joe,je,k)
     E_vx(k) = E_vx(k) + E(joe,je,k)
     E_vt(jent) = E_vt(jent) + E(joe,je,k)
     E_ss_vt(joe,jent) = E_ss_vt(joe,jent) + E(joe,je,k)
     E_ss(joe) = E_ss(joe) + E(joe,je,k)
    end do      
   ! write(*,*) 'k, je, Evap = ', k, je, E(0,je,k), E(1,je,k)
   end do
  end do
  E_canopy = E_canopy / lambda/18*1000.  ! Evaporation rate in mmol H20 s-1


!  Normalisation of Es by leaf area

  do k=1,nveg
   do je=1,nje(k)
    E_vt_vx(je,k)=E_vt_vx(je,k)/S_vt_vx(je,k)
   end do
   E_vx(k)=E_vx(k)/S_vx(k)
  end do
  do jent=1,nent
   do joe=0,1
    E_ss_vt(joe,jent)=E_ss_vt(joe,jent)/S_ss_vt(joe,jent)
   end do
   E_vt(jent)=E_vt(jent)/S_vt(jent)
  end do
  do joe=0,1
   E_ss(joe)=E_ss(joe)/S_ss(joe)
  end do
  E_canopy = E_canopy / S_canopy
  H_canopy = H_canopy / S_canopy


!  Distribution of leaf temperature at canopy scale

!  do k=1,nveg
!   do je=1,nje(k)
!    do joe=0,1
!     tsclass=int(ts(joe,je,k))+1
!     Sts(nume(je,k),tsclass)=Sts(nume(je,k),tsclass)+S_detailed(joe,je,k)
!    end do
!   end do
!  end do



! Deallocation of local arrays used in subroutine eb_doall
  !deallocate(E)     ! Latent heat flux by shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(raco2)    ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport
!  deallocate(gs)     ! Stomatal conductance (two sides) (m s-1) of shaded/sunlit are of each vegetation type in each voxel
  deallocate(omega_factor) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel
  deallocate(rni)    ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(rayirt)   ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

 end subroutine eb_doall2
!------------------------------------------------------------------end  eb_doall2

 subroutine Jarvis_stomata(jent,leaf_nitrogen,par_irrad,ca,HRsol,leaf_temp,VPDair,ga,rsi,drsi)

 use vegetation_types

!  Jarvis model (1976), modified by Le Roux et al. (1999) for inclusion of Na effect
!  Stomatal conductance: gs, in m s-1

!  Input variables
  integer :: jent  ! Vegetation type #, needed to get the suitable gs response parameters.
  real  :: leaf_nitrogen ! leaf nitrogen content Na (g m-2)
  real  :: par_irrad, ca, leaf_temp, VPDair, ga ! microclimate variables sensed by the leaf, plus leaf boundary conductance as needed in solving coupling between gs and VPD
  real  :: HRsol   !Relative Soil Humidity   Ngao 02/2012 
  real  :: VPDthreshold ! VPD value below which fgsVPD = cte = fgsVPD(VPDthreshold)

!  Output variables: stomatal conductance (m s-1) / resistance (s m-1), and derivatives with regard to leaf temperature
  real  :: gsi, rsi, dgsi, drsi
  
  
  real  :: gsHRsol  ! response function of gs to HRsol  - Ngao 02/2012
  real  :: aHRsol,bHRsol    ! coeffs response function of gs to HRsol  - Ngao 02/2012
  real  :: gsmax    ! Maximum gs (m s-1), as a function of leaf nitrogen content Na (g m-2)
  real  :: fgsPAR   ! Reducing factor of PAR irradiance on gs
  real  :: fgsCA    ! Reducing factor of air CO2 partial pressure on gs
  real  :: fgsLT    ! Reducing factor of leaf temperature on gs
  real  :: fgsVPD0   ! Reducing factor of VPD on gs, for leaf VPD = 0
  real  :: fgsVPDair  ! Reducing factor of VPD on gs, for leaf VPD = air VPD
  real  :: fgsVPDt   ! Reducing factor of VPD on gs, for leaf VPD = VPDthreshold
  real  :: gsVPD0   ! Stomatal conductance at leaf VPD = 0
  real  :: gsVPDair   ! Stomatal conductance at leaf VPD = air VPD

  real  :: dfgsLT   ! Derivative of fgsLT with regard to leaf temperature
  real  :: dgsVP0   ! Derivative of gsVP0 with regard to leaf temperature
  real  :: dgsVPair   ! Derivative of gsVPair with regard to leaf temperature
  real  :: des    ! Derivative of saturating water vapour pressure with regard to leaf temperature

!  Step #1: maximum gs, as a function of leaf nitrogen content Na (g m-2)
!  AgsN = 2.002 * 1.e-3  !Paramètres pour Noyer
!  BgsN = 0.740 * 1.e-3
      gsmax=AgsN(jent,1)*leaf_nitrogen+AgsN(jent,2)

!  Step #2: effect of PAR irradiance on gs, i.e. reducing factor : fgsPAR
  select case (i_gsPAR(jent)) ! type of equation for gs response to PAR

   case (1)  ! gs=f(PAR) : 2nd order polynomial function

!   AgsPAR = -3.752 * 1.e-7  ! Paramètres Noyer (ajustement données jeune Noyer a CO2 ambiant (Juillet 2000)
!   BgsPAR = 1.105 * 1.e-3
!   CgsPAR = 0.183

   if (par_irrad.gt.1500.) then
    fgsPAR=1.00
   else
    fgsPAR=AgsPAR(jent,1)*par_irrad**2+AgsPAR(jent,2)*par_irrad+AgsPAR(jent,3)
   endif

   case (2) ! gs=f(PAR) : hyperbola (a PAR + b) / (c PAR +d) : i.e. 4 parameters

   fgsPAR=(AgsPAR(jent,1)*par_irrad+AgsPAR(jent,2))/(AgsPAR(jent,3)*par_irrad+AgsPAR(jent,4))

   case (3) ! gs=f(PAR) : function (a PAR² + b PAR + c) / (d PAR² + e PAR + f) : i.e. 6 parameters

   fgsPAR=(AgsPAR(jent,1)*par_irrad**2+AgsPAR(jent,2)*&
   &par_irrad+AgsPAR(jent,3))/(AgsPAR(jent,4)*par_irrad**2+&
   &AgsPAR(jent,5)*par_irrad+AgsPAR(jent,6))

   case (4) ! gs=f(PAR) : function (a sqrt(PAR) + b) / (c PAR + d sqrt(PAR) + e) : i.e. 5 parameters

   fgsPAR=(AgsPAR(jent,1)*sqrt(par_irrad)+AgsPAR(jent,2))/(AgsPAR(jent,3)*&
   &par_irrad+AgsPAR(jent,4)*sqrt(par_irrad)+AgsPAR(jent,5))

   case (5) ! gs=f(PAR) : function a / (b + [(PAR-c)/d]²) : i.e. 4 parameters

   fgsPAR= AgsPAR(jent,1)/(AgsPAR(jent,2)+&
   &((par_irrad-AgsPAR(jent,3))/AgsPAR(jent,4))**2)

   case (6)  ! LASER/F Case - MARC May 2018
   
   fgsPAR = (0.55*2*(par_irrad/1.93)/30.0)/11.2 
   fgsPAR= amax1(0.000001,(fgsPAR+150.0/5000.0)/(1+fgsPAR))   
!   if (par_irrad.le.1e-1) then
!    fgsPAR = 0.000001
!   endif
   
   case default

   fgsPAR=1.00

  end select

!  Step #3: effect of partial CO2 pressure on gs, i.e. reducing factor fgsCA
  select case (i_gsCA(jent))    ! type of equation for gs response to CO2 partial pressure

   case (1) ! gs=f(ca) : 2nd order polynomial function

!   AgsCA = 2.32e-4    ! Paramètres Noyer de Plauzat
!   BgsCA = -4.02e-2
!   CgsCA = 2.07

   fgsCA=AgsCA(jent,1) * ca**2 + AgsCA(jent,2) * ca + AgsCA(jent,3)     

   case (2)  ! LASER/F Case - MARC May 2018
   
   fgsCA= 0.8 

   case default

   fgsCA=1.00

  end select

!  Step #4: effect of leaf temperature on gs, i.e. reducing factor fgsLT
  select case (i_gsLT(jent))    ! type of equation for gs response to leaf temperature

   case (1) ! gs=f(leaf_temp) : 2nd order polynomial function

!   AgsLT = -4.82e-3   ! Paramètres Noyer de Plauzat
!   BgsLT = 0.24165
!   CgsLT = -2.029

   fgsLT=amax1(AgsLT(jent,1)*leaf_temp**2+AgsLT(jent,2)*leaf_temp+AgsLT(jent,3),0.05)

   case (3) ! gs=f(leaf_temp) : function (a LT² + b LT + c) / (d LT² + e LT + f) : i.e. 6 parameters

   fgsLT=(AgsLT(jent,1)*leaf_temp**2+AgsLT(jent,2)*leaf_temp+AgsLT(jent,3))/&
   &(AgsLT(jent,4)*leaf_temp**2+AgsLT(jent,5)*leaf_temp+AgsLT(jent,6))

   case (4) ! gs=f(leaf_temp) : function (a sqrt(LT) + b) / (c LT + d sqrt(LT) + e) : i.e. 5 parameters

   fgsLT=(AgsLT(jent,1)*sqrt(leaf_temp)+AgsLT(jent,2))/&
   &(AgsLT(jent,3)*leaf_temp+AgsLT(jent,4)*sqrt(leaf_temp)+AgsLT(jent,5))

   case (5) ! gs=f(leaf_temp) : function a / (b + [(LT-c)/d]²) : i.e. 4 parameters

   fgsLT=AgsLT(jent,1)/(AgsLT(jent,2)+&
   &((leaf_temp-AgsLT(jent,3))/AgsLT(jent,4))**2)

   case (6)  ! LASER/F Case - MARC May 2018
   
   fgsLT= amax1(0.001,1-0.0016*(298.15-(273.15+leaf_temp))**2) 
   
   case default

   fgsLT=1.00

  end select

!  Step #5: effect of air VPD on gs: a little bit more complicated !
!      because gs does not respond to air VPD, but to leaf surface VPD
!      Coupling between VPD and gs must thus be solved.
!      Gs response to VPD is assumed to be linear: fgsVPD = AgsVPD* VPDleaf + BgsVPD
!      Improved solving as reported in SAFE booklet (H. Sinoquet, 23 dec 2002)
!      gs = (1/2) [ square_root{ [ga - gs(VPDleaf=0)]² + 4 ga gs(VPDleaf=VPDair) } - [ga - gs(VPDleaf=0)]  ]
!    Two major advantages:
!  1- Intermediate variables have some biological meaning
!  2- Analytical derivation of gs with regard to leaf temperature is possible

!  AgsVPD = -1.8e-4  ! Paramètres Noyer de Plauzat
!  BgsVPD = 1.18

!  Addendum 09 June 2004: Threshold value for VPD, i.e. below threshold value fgsVPD= cte = fgsVPD(VPDthreshold)
!          For Noyer de Plauzat: VPDthreshold = 1000 Pa

  VPDthreshold=AgsVPD(jent,3)
  fgsVPDt = AgsVPD(jent,1) * VPDthreshold + AgsVPD(jent,2)

  fgsVPD0 = amin1(AgsVPD(jent,1) * 0. + AgsVPD(jent,2), fgsVPDt)
  gsVPD0 = gsmax * fgsPAR * fgsCA * fgsLT * fgsVPD0

  fgsVPDair = amin1(amax1(AgsVPD(jent,1) * VPDair + AgsVPD(jent,2) , 0.05), fgsVPDt)
  gsVPDair = gsmax * fgsPAR * fgsCA * fgsLT * fgsVPDair
  !write(*,*) 'gsi  =',gsmax ,fgsPAR , fgsCA , fgsLT , fgsVPDair
  
  ! LASER/F Case - MARC May 2018
  fgsVPD0 = 1.0 
  gsVPD0 = gsmax * fgsPAR * fgsCA * fgsLT * fgsVPD0
                                                     
  VPDkg =  (0.622*VPDair)/((1016*100)-0.378*VPDair)
  fgsVPDair =amax1(0.001,1-0.04*VPDkg*1000)
  gsVPDair = gsmax * fgsPAR * fgsCA * fgsLT * fgsVPDair  
  ! LASER/F Case - MARC May 2018
    
 
!Ngao 02/2012: Adding effect of soil humidity on gs
  gsHRsol = 0.00
  aHRsol = 0.9688
  bHRsol = -0.4022
  if (HRsol.le.abs(bHRsol/aHRsol)) then !  bHRsol/aHRsol sould be <1
      gsHRsol = aHRsol*HRsol+bHRsol
  endif
  
  gsi=0.5*(sqrt((ga-gsVPD0)**2+4.*ga*gsVPDair) - (ga-gsVPD0) ) + gsHRsol
   
!Ngao 02/2012: Adding effect of soil humidity on gs  
  if (gsi.lt.0) gsi=10e-8
!  gsi=0.5*(sqrt((ga-gsVPD0)**2+4.*ga*gsVPDair) - (ga-gsVPD0) )
  rsi=1/gsi

  
!  Step #6: Derivative of gs with regard to leaf temperature
!  Analytical solution, as found in SAFE booklet (H. Sinoquet, 23 dec 2002)

!  Derivative of fgsts with regard to leaf temperature
  select case (i_gsLT(jent))    ! type of equation for gs response to leaf temperature
   case (1) ! gs=f(leaf_temp) : 2nd order polynomial function
    dfgsLT=2*AgsLT(jent,1)*leaf_temp+AgsLT(jent,2)
    if (fgsLT.le.0.05) then
     dfgsLT=0.
    endif
   case default
    dfgsLT=0.
  end select

!  Derivative of gsVPD0 with regard to leaf temperature
  dgsVPD0=gsvpd0*dfgsLT/fgsLT

!  Saturating water vapor pressure, es, at temperature ts: Tetens' formula (1930), en Pa
!  and its derivative des, with regard to temperature ts
!  es=610.78*exp((17.27*leaf_temp)/(237.3+leaf_temp))
  des=610.78*17.27*237.3/((237.3+leaf_temp)**2)*exp((17.27*leaf_temp)/(237.3+leaf_temp))
!  Note that des is needed, as it it also the derivative of VPDair with regard to leaf temperature

!  Derivative of gsVPDair with regard to leaf temperature
  dfgsVPDair=AgsVPD(jent,1)*des
  if ((fgsVPDair.gt.0.05).and.(VPDair.gt.VPDthreshold)) then
   dgsVPDair=gsVPDair*(dfgsLT/fgsLT + dfgsVPDair/fgsVPDair)
  else
   dgsVPDair=gsVPDair*(dfgsLT/fgsLT)
  endif


  dgsi=sqrt((ga-gsVPD0)**2+4.*ga*gsVPDair)
  dgsi=0.5*(2.*dgsVPD0*(gsVPD0-ga)+4.*ga*dgsVPDair)/dgsi
  dgsi=0.5*(dgsVPD0+dgsi)

  drsi = - dgsi / gsi**2


 end subroutine Jarvis_stomata

 subroutine eb_destroy

  if (allocated(E_vt_vx))  deallocate(E_vt_vx) 
  !write(*,*) '...deallocate(E_vt_vx)  ok '
  if (allocated(E_vx))   deallocate(E_vx)   
  !write(*,*) '...deallocate(E_vx)  ok '
  if (allocated(E_vt))   deallocate(E_vt)   
  !write(*,*) '...deallocate(E_vt)   ok '
  if (allocated(E_ss_vt))  deallocate(E_ss_vt)   
  !write(*,*) '...deallocate(E_ss_vt)  ok '
  if (allocated(E))  deallocate(E)      
  !write(*,*) '...deallocate(E)  ok '
  if (allocated(ts))   deallocate(ts)   
  !write(*,*) '...deallocate(ts)   ok '
  if (allocated(ts_iter))   deallocate(ts_iter)   
  !write(*,*) '...deallocate(ts_iter)   ok '
  if (allocated(gs))   deallocate(gs)   
  !write(*,*) '...deallocate(gs)  ok '
  if (allocated(rco2))   deallocate(rco2)
  !write(*,*) '...deallocate(rco2) ok '

!  if (allocated(Sts))   deallocate(Sts)
!  write(*,*) '...deallocate(Sts) ok '

 end subroutine eb_destroy
!---------------------------------------
! Tests whether the two functions values bracket a root -- i.e., have different signs
 function bracketsRoot(fa,fb) result(tf)
    logical :: tf
    real :: fa,fb
    tf = sign(fa,fb)/=fa
 end function bracketsRoot
 
! One dimensional test functions
 function EnergBilan(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,leaf_nitrogen,par_irrad,caref,&
 &HRsol,VPDair,x)
    implicit none
    real :: EnergBilan     
    real :: sigma, rn, rho,cp,taref,rh
    real :: gamma, ga,earef,leaf_nitrogen,par_irrad,caref,HRsol,VPDair
    integer :: jent 
    real, intent(in) :: x

    EnergBilan =  rn - RayoIR(sigma,x) - Convection(rho,cp,taref,rh,x)- &
    &Evapotranspi(rho*cp/gamma,ga,jent,earef,leaf_nitrogen,par_irrad,caref,HRsol,VPDair,x)    
  end function 
  
 function Convection(rho,cp,taref,rh,x)
    implicit none
    real :: Convection
    real :: rho,cp,taref,rh
    real, intent(in) :: x
    Convection =  (rho*cp)*(x-taref)/rh
  end function
    
 function Evapotranspi(alpha,ga,jent,earef,leaf_nitrogen,par_irrad,caref,HRsol,VPDair,x)
    implicit none
    real :: Evapotranspi
    real :: es, rss, alpha, ga,earef,leaf_nitrogen,par_irrad,caref,HRsol,VPDair
    real :: ra,rv,rsi,drsi
    integer :: jent 
    real, intent(in) :: x
    
    !    Saturating water vapor pressure, es, at temperature ts: Tetens' formula (1930), en Pa
    !    and its derivative des, with regard to temperature ts
    es=610.78*exp((17.27*x)/(237.3+x))
  
    !    Stomatal resistance (in s m-1) / conductance (in m s-1)
    !    rss:  upper side stomatal resistance
    !    rsi:  lower side stomatal resistance
    !    gs :  lower side stomatal conductance

    rss=10000.    ! Arbitrary high value

    !write(*,*) 'call Jarvis_stomata avant'
    call Jarvis_stomata(jent,leaf_nitrogen,par_irrad,caref,HRsol,x,VPDair,ga,rsi,drsi)
    !write(*,*) 'Jarvis  - rsi =',rsi
    !write(*,*) 'call Jarvis_stomata apres'

    !    Total resistances, i.e. boundary layer + stomatal and 2 sides, in s m-1
    !    rv : water vapour transfert
    !    rh : heat transfert
    ra = 1.0/ga
    if (es.lt.earef) then   ! Saturation at leaf surface (i.e. dew formation)
     rv=ra/2.
    else
     rv=(rss+ra)*(rsi+ra)/(rss+rsi+2.*ra)
    endif
    !    2- Latent heat flux: evap, in W m-2 
    Evapotranspi= alpha*(es-earef)/rv  
!    if (par_irrad.lt.0.1) then
!         Evapotranspi = 0.0
!    endif
  end function  
  
 function RayoIR(sigma,x)
    ! Rayo IRT in W per meter square
    implicit none
    real :: RayoIR
    real  :: sigma
    real, intent(in) :: x
    RayoIR =  2.*sigma*(x+273.15)**4 
  end function
   
 subroutine sub_brent(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,leaf_nitrogen, par_irrad,caref,&
 &HRsol,VPDair,x,f,a_in,b_in,toler_in,maxiter_in,fa_in,fb_in,xtoler_in,printmod_in)
    !! From  https://sites.google.com/site/greygordon/code
    implicit none    
    real :: sigma, rn,rho,cp,taref,rh
    real :: gamma,ga,earef,leaf_nitrogen, par_irrad,caref,HRsol,VPDair
    integer :: jent 
    real, intent(out) :: x
    interface
        function f(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,leaf_nitrogen, par_irrad,caref,&
        &HRsol,VPDair,x)
        implicit none
        real :: sigma, rn ,rho,cp,taref,rh 
        real :: gamma,ga,earef,leaf_nitrogen, par_irrad,caref,HRsol,VPDair 
        integer :: jent 
        real, intent(in) :: x
        real :: f
        end function f
    end interface
    real, intent(in) :: a_in,b_in
    real, intent(in), optional :: toler_in,fa_in,fb_in,xtoler_in
    integer, intent(in), optional :: maxiter_in, printmod_in
    ! local
    real, parameter :: machep = epsilon(0.0)
    real :: a,b,c,fa,fb,fc,toler,xtoler,e,d,m,p,q,tol,t,r,s
    integer :: maxiter,printmod,iter
    character(len=6) :: step

    ! Set of get parameters
    toler = 0.0; if (present(toler_in)) toler = toler_in ! Better to use custom toler here
    xtoler = xtoler_def; if (present(xtoler_in)) xtoler = xtoler_in
    maxiter = maxiter_def; if (present(maxiter_in)) maxiter = maxiter_in    
    printmod = printmod_def; if (present(printmod_in)) printmod = printmod_in

    ! Set the user chosen tolerance t to xtoler
    if (xtoler<0.0) then
        print*,'WARNING: xtoler must be positive. Resetting xtoler.'
        xtoler = 0.0
    end if
    t = xtoler
    
    ! Get initial bracket
    a=a_in
    b=b_in
    if (present(fa_in)) then
        fa = fa_in
    else
        fa = f(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,leaf_nitrogen, par_irrad,caref,&
        &HRsol,VPDair,a)
    end if
!    write(*,*) 'f(a)', fa
    
    if (present(fb_in)) then
        fb = fb_in
    else
        fb = f(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,leaf_nitrogen, par_irrad,caref,&
        HRsol,VPDair,b)
    end if   
 !  write(*,*) 'f(b)', fb

    ! Test whether root is bracketed
    if (.not. bracketsRoot(fa,fb)) then
        if (abs(fa)<abs(fb)) then
            write(*,*) 'brent: WARNING: root is not bracketed, returning best endpoint a'
            x = a
        else
            write(*,*) 'brent: WARNING: root is not bracketed, returning best endpoint b'
            x = b
        end if
        return
    end if

    step = 'init'

    ! At any point in time, b is the best guess of the root, a is the previous value of b, 
    ! and the root is bracketed by b and c.
    do iter = 1,maxiter

        if (iter==1 .or. (fb>0.0 .and. fc>0.0) .or. (fb<=0.0 .and. fc<=0.0)) then
            c = a
            fc = fa
            e = b - a
            d = e
        end if

        ! If c is strictly better than b, swap b and c so b is the best guess. 
        if (abs(fc)<abs(fb)) then
            a = b
            b = c
            c  = a
            fa = fb
            fb = fc
            fc = fa
        end if

        ! Set the tolerance. Note: brent is very careful with these things, so don't deviate from this.
        tol = 2.0*machep*abs(b) + t

        ! Determine what half the length of the bracket [b,c] is
        m = .5*(c-b)

        ! If taking a bisection step would move the guess of the root less than tol, then return b the best guess.
        if ((abs(m)<=tol) .or. (fb==0.0)) then
            x = b
            return
        end if

        ! Display info
        if (printmod>0 .and. mod(iter,printmod)==0) write(*,"(A,i5,A,e13.5,A,e13.5,A,A)") &
          'brent: iter ',iter,' b',b,' fb',fb,' ',step

        ! If still here, then check whether need to do bisection or can do interpolation
        if ((abs(e)>=tol) .and. (abs(fa)>abs(fb))) then
            s = fb/fa
            if (a/=c) then
                ! Inverse quadratic interpolation
                q = fa/fc
                r = fb/fc
                p = s*(2.0*m*q*(q-r) - (b-a)*(r-1.0))
                q = (q-1.0)*(r-1.0)*(s-1.0)
                
                step = 'quad'
            else
                ! Linear interpolation
                p = 2.0*m*s
                q = 1.0-s

                step = 'linear'
            end if

            ! Ensure p is positive
            if (p<=0.0) then
                p = -p
            else
                q = -q
            end if

            s = e
            e = d
            if ((2.0*p>=3.0*m*q-abs(tol*q)) .or. &
                (p>=abs(.5*s*q))) then
                ! Interpolation step failed to produce good step, bisect instead
                e = m
                d = m ! m is half the distance between b and c
                step = 'bisect'
            else
                !  Do interpolation step (either quadratic or linear)
                d = p/q
            end if
        else

            ! Do bisection step
            e = m 
            d = m
            
        end if

        ! Get new points. 
        !! Replace a (the old b) with b.
        a = b
        fa = fb

        !!! Increment b by d if that is greater than the tolerance. O/w, increment by tol.
        if (abs(d)<=tol) then
            ! m is .5*(c-b) with the bracket either [b,c] or [c,b]. 
            if (m > 0.0) then
                ! If m>0.0, then bracket is [b,c] so move towards c by tol
                b = b + tol
            else
                ! If m<=0d0, then bracket is [c,b] so move towards c by tol
                b = b - tol
            end if
        else
            b = b + d
        end if

        !!! Evaluate at the new point
        fb = f(rn,sigma,rho,cp,taref,rh,gamma,ga,jent,earef,leaf_nitrogen, par_irrad,caref,&
        &HRsol,VPDair,b)

        ! Check my custom tolerance 
        if (abs(fb)<toler) then
            x = b
            return
        end if
            
    end do

 end subroutine sub_brent

end module Energy_balance

!------------------------------------------------------------------------------
