!------------------------------------------------------------------------------

module micrometeo

character*6 spec_mmeteo  ! for mmeteo


! Input meteorological data at current time step

integer :: ntime, nbli
real :: day,hour    ! day and hour
real, allocatable :: glob(:), diff(:), direct(:), dsg (:) ! global, diffuse and direction radiation in band iblo, D/G ratio in band iblo
real :: ratmos      ! atmospheric radiation
real :: tsol,taref,earef,caref ! soil temperature, air temperature, water vapour pressure in the air (Pa), CO2 partial pressure in the air (Pa)
real :: HRsol         !Relative Soil Humidity   Ngao 02/2012 
real, allocatable :: uref(:)  ! wind speed, in each horizontal layer (jz=1,njz)
real, allocatable :: tabMeteo(:,:)  ! Meteo data

integer :: ntimemax
logical  :: endmeteo     ! TRUE if end of mmeteo file has been reached
logical :: truesolartime ! ajout mwoussen 23/03/2022, l'heure en entrée est l'heure solaire ou locale

contains

 subroutine mm_initiate

!  Allocate arrays of module micrometeo

  use grid3D
  use vegetation_types

  call mm_destroy

  allocate(glob(nblomin))
  allocate(diff(nblomin))
  allocate(direct(nblomin))
  allocate(dsg(nblomin))

  allocate(uref(njz))

  endmeteo=.FALSE.

 end subroutine mm_initiate

 subroutine mm_read(ntime,nbli)

  use grid3D
  use vegetation_types

  !dimension tabMeteo(nbli,13)

  character*17 pathMeteo
  character*6 spec
  integer ii
  !write(*,*) '...mm_read : ',ntime
  !write(*,*) 'tabMeteo : ',(tabMeteo(ntime,ii),ii=1,13)
  !call mm_initiate
    !write(*,*) 'taille tabmeteo : ',size(tabMeteo)
    !write(*,*) 'shape tabmeteo : ',shape(tabMeteo),tabMeteo(1,1)
    ii = 1
    day=tabMeteo(ntime,ii)
    !write(*,*) '...mm_read nblomin : ',nblomin
    ii = ii+1
    hour=tabMeteo(ntime,ii)
    do iblo=1,nblomin
        ii = ii+1
        glob(iblo)=tabMeteo(ntime,ii)
!        write(*,*) 'ii,tabMeteo(ntime,ii) =',ii,tabMeteo(ntime,ii)
        ii = ii+1
        diff(iblo)=tabMeteo(ntime,ii)
    end do
    ii = ii+1
    ratmos=tabMeteo(ntime,ii)
!    write(*,*) '**********'
!    write(*,*) 'ii,tabMeteo(ntime,ii) =',ii,tabMeteo(ntime,ii)
!    write(*,*) 'ratmos =',ratmos
    ii = ii+1
    tsol=tabMeteo(ntime,ii)
    ii = ii+1
    taref=tabMeteo(ntime,ii)
!    write(*,*) '**********'
!    write(*,*) 'ii,tabMeteo(ntime,ii) =',ii,tabMeteo(ntime,ii)
!    write(*,*) 'taref =',taref
    ii = ii+1
    earef=tabMeteo(ntime,ii) 
!    write(*,*) '**********'
!    write(*,*) 'ii,tabMeteo(ntime,ii) =',ii,tabMeteo(ntime,ii)
!    write(*,*) 'earef =',earef
    ii = ii+1
    caref=tabMeteo(ntime,ii)
    ii = ii+1
    urefref=tabMeteo(ntime,ii)
    ii = ii+1                       !Relative Soil Humidity   Ngao 02/2012 
    HRsol=tabMeteo(ntime,ii)        !Relative Soil Humidity   Ngao 02/2012  set to 1 by default (no stress)

    !write(*,*) 'day,hour =',day,hour ,(glob(iblo),diff(iblo),iblo=1,nblomin), ratmos,tsol,taref,earef,caref,urefref

!   Rem: L'azimut 0 est d�fini pour la direction SUD,
!      i.e. un rayon avancant vers le NORD, donc les X > 0
!    L'azimut 90 est d�fini pour la direction OUEST,
!    i.e. un rayon avancant vers l'EST, donc les Y > 0

   !write(*,*)
   !write(*,*) '----------------------------------------'
   !write(*,*) 'Step: ',ntime

   do iblo=1,nblomin
    if (glob(iblo).gt.0.) then
     if (glob(iblo).lt.diff(iblo)) then
      !write(*,*) 'Warning: Incident radiation in waveband #',iblo,' is lesser than value of diffuse radiation:'
      !write(*,*) glob(iblo),' < ',diff(iblo)
      !write(*,*) 'Will be set to value of incident diffuse radiation:', diff(iblo)
!      pause
      glob(iblo)=diff(iblo)
     endif
     direct(iblo)=glob(iblo)-diff(iblo)
     dsg(iblo)=diff(iblo)/glob(iblo)
    else
     !write(*,*) 'Warning: Incident radiation in waveband #',iblo,' is negative or zero:', glob(iblo)
     !write(*,*) 'Will be set to zero'
!     pause
     glob(iblo)=0.
     diff(iblo)=0.
     direct(iblo)=0.
     dsg(iblo)=1.
    endif
   end do

   do jz=1,njz
    uref(jz) = urefref
   end do
   !write(*,*) 'end meteo'


 end subroutine mm_read

 subroutine mm_destroy

!  Deallocate arrays of module micrometeo

  if (allocated(glob))  deallocate(glob)
  if (allocated(diff))  deallocate(diff)
  if (allocated(direct)) deallocate(direct)
  if (allocated(dsg))  deallocate(dsg)

  if (allocated(uref))  deallocate(uref)

 end subroutine mm_destroy


end module micrometeo

!------------------------------------------------------------------------------
