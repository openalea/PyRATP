!---------------------------------------------------------------

module MinerPheno

real, allocatable :: tbody(:)     ! for each voxel k : body temperature at current time step
real, allocatable :: dev_rate(:)    ! for each voxel k : developmental rate at current time step
real, allocatable :: sum_dev_rate(:)  ! for each voxel k : cumulated developmental rate : larva is out when sum_dev_rate(k)=1
real, allocatable :: sum_time(:)    ! for each voxel k : number of time steps needed for larva development in voxel k
real, allocatable :: sum_tair(:)    ! for each voxel k : air temperature degree-hours needed for larva development in voxel k
integer, allocatable :: larvadeath(:)  ! for each voxel k : time step when the larva dies (in case of high temperature)
integer, allocatable :: larvaout(:)   ! for each voxel k : time step when the larva has terminated its development
real     :: sum_taref    ! air temperature degree-hours counter
integer    :: nlarvadead    ! number of dead larvae at the end of the simulation
integer    :: nlarvaout    ! number of out larvae at the end of the simulation

contains

 subroutine miph_doall

! Computation of the miner phenology in each voxel.occupied by a mined leaf: see Pincebourde et al. 2007. Journal of Animal Ecology.
!   - compute larva body temperature (at each time step)
!   - compute developmental rate (at each time step)
!   - sum up developmental rate
!   - compute larva mortality (T° > 42° for only one time step)

  use constant_values
  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo
  use shortwave_balance
  use energy_balance

  real :: T(2), C(3)   ! Constantes in developmental rate equation (eqn 4, in SP et al. 2007)
  real :: rho25, DHA, TL, DHL, TH, DHH
  real :: tbodyK ! temperature en Kelvin
  tbody=0.
  dev_rate=0.

  !C(1)=0.047   ! lower development (day-1)  values from Baumgarnter & Severini (1987)
  !C(2)=0.066   ! rate of increase
  !C(3)=0.047   ! temperature range
  T(1)=5.2    ! Lower threshold (°)
  T(2)=42.0   ! Upper threshold (°)
  rho25 = 0.15266600
  DHA = 4526.55271161
  TL = 284.30498226
  DHL = -60116.20158705
  TH = 307.27912758
  DHH = 99837.64527791


  sum_taref=sum_taref+(taref-t(1))  ! Sum of air temperature: Lower threshold for developmental rate is included

  do k=1,nveg   ! Boucle sur les voxels occupés par une feuille minée
    do je=1,nje(k)
     jent=nume(je,k)
     if (ismine(jent).eq.1) then  ! Le voxel contient des feuilles minées
      if ((larvadeath(k).eq.0).and.(larvaout(k).eq.0)) then ! larva in voxel k is still alive and not yet out


!  Computing body temperature

       do joe=0,1
        fFW=0.0034*parirrad(joe,je,k) + 0.0293     ! PAR irradiance function for feeding windows
        fGP=0.0013*parirrad(joe,je,k) - 0.017     ! PAR irradiance function for green patches
        tb=ts(joe,je,k) + 0.4*fFW + 0.6*fGP      ! Time spent by the larva under Feeding Windows is assumed to be 40%
        tbody(k)=tbody(k)+tb*S_detailed(joe,je,k)
       end do
       tbody(k)=tbody(k)/S_vt_vx(je,k)  ! Only on temperature is computed in each voxel, i.e. no distinction between shaded and sunlit area



!  Computing developmental rate (dev_rate, h-1): Boucle sur les voxels occupés par une feuille minée: Eqn 4 SP et al. 2007

       if ((tbody(k).ge.t(2)).and.(larvadeath(k).eq.0)) then    ! body temperature is too high, larva dies
        larvadeath(k)=ntime
        nlarvadead=nlarvadead+1    ! one more dead larva
       else if (tbody(k).le.t(1)) then  ! body temperature is too low, larva does not grow
        dev_rate(k)=0.
       else
        tbodyK = tbody(k) +273.2
        !dev_rate(k)=c(1)*(exp(c(2)*(tbody(k)-t(1)))-exp(c(2)*(t(2)-t(1))-(t(2)-tbody(k))/c(3)))/24.
        dev_rate(k) = rho25*(tbodyK)/298.*exp(DHA/1.937 * (1/298.-1/(tbodyK)))
        dev_rate(k) = dev_rate(k)/(1+exp(DHL/1.937*(1/TL-1/tbodyK))+exp(DHH/1.937*(1/TH-1/tbodyK)))
        dev_rate(k) = dev_rate(k)/24.
       endif
       !!!!!!if (k.eq.1) write(*,*) taref, tbody(k), dev_rate(k)

!  Summing up (from first time step: ntime=1) : cumulated developmental rate, cumulated body temperature, cumulated air temperature

       sum_dev_rate(k)=sum_dev_rate(k)+dev_rate(k)
       if ((sum_dev_rate(k).gt.1.).and.(larvaout(k).eq.0)) then
        larvaout(k)=ntime
        nlarvaout=nlarvaout+1    ! one more larva out
        sum_tair(k)=sum_taref    ! air temperature degree-hours corresponding to stage L5 in voxel k
       endif

      endif
     endif
    end do
  end do



 end subroutine miph_doall


 subroutine miph_allocate

  use grid3D

  call miph_destroy

  allocate(tbody(nveg))
  allocate(dev_rate(nveg))
  allocate(sum_dev_rate(nveg))
  allocate(sum_tair(nveg))
  allocate(larvadeath(nveg))
  allocate(larvaout(nveg))

  sum_dev_rate=0.
  sum_tair=0.
  sum_taref=0.
  larvadeath=0
  larvaout=0
  nlarvadead=0
  nlarvaout=0


 end subroutine miph_allocate


 subroutine miph_destroy

  if (allocated(tbody))    deallocate(tbody)
  if (allocated(dev_rate))   deallocate(dev_rate)
  if (allocated(sum_dev_rate))  deallocate(sum_dev_rate)
  if (allocated(sum_tair))   deallocate(sum_tair)
  if (allocated(larvadeath))   deallocate(larvadeath)
  if (allocated(larvaout))   deallocate(larvaout)

 end subroutine miph_destroy


end module MinerPheno

!-----------------------------------------------------------------------------------------
