!------------------------------------------------------------------------------

module vegetation_types

character*6 spec_vegetation  ! for vegetation types


! Remarque : Le nombre de composantes est donn� par la d�finition de la grille
!     NENT est donc un param�tre de grid3D, pas de vegetation_types
!     mais vegetation_types construit les tableaux de param�tres d'un ensemble de NENT composantes de v�g�tation

!  Parameter of foliage dispersion within voxels (1: random, <1: clumped; >1: regular)
real, allocatable :: mu(:)

!  Inclination distribution of vegetation types
integer :: nbinclimax ! Maximal number of inclination classes in the input file
integer, allocatable :: nbincli(:) ! Number of inclination classes for vegetation type #jent, jent=1,nent
integer :: nbinclivox ! ajout mwoussen 06/04/2022 Number of inclination classes if pervoxel=true, same number of class in each voxel
real, allocatable :: distinc(:,:) ! % leaf area in leaf inclination angle class for vegetation type #jent, jent=1,nent
real, allocatable :: distincvox(:,:,:) ! ajout mwoussen 06/04/2022 % leaf area in leaf inclination angle class for vegetation type #jent, jent=1,nent and voxel k=1,nveg
logical :: pervoxel ! ajout mwoussen 06/04/2022 indique une distribution par voxel et non globale

! Optical properties of vegetation types
integer :: nblomin  ! Minimal number of wavelength bands in the input file
integer, allocatable :: nblo(:) ! Number of wavelenght bands for vegetation type #jent, jent=1,nent
real, allocatable :: rf(:,:) ! average value of leaf reflectance and transmittance, one value per wavelength band

! Parameters of leaf boundary conductance ga: ga: ga = Aga(jent,1)* wind_speed + Aga(jent,2)
real, allocatable :: Aga(:,:)

! Jarvis'model parameters for stomatal conductance gs
real, allocatable :: AgsN(:,:)  ! effect of leaf nitrogen: gs (s m-1) = A1*Na (g m-2) + A2
integer, allocatable :: i_gsPAR(:) ! effect of leaf PAR irradiance: gs (s m-1) = f(PAR, �mol m-2 s-1)
real, allocatable  :: AgsPAR(:,:)
integer, allocatable :: i_gsCA(:) ! effect of air CO2 partial pressure: gs (s m-1) = f(CA, Pa)
real, allocatable  :: AgsCA(:,:)
integer, allocatable :: i_gsLT(:) ! effect of leaf temperature: gs (s m-1) = f(LT, Pa)
real, allocatable  :: AgsLT(:,:)
real, allocatable :: AgsVPD(:,:)  ! effect of leaf VPD: gs (s m-1) = A1*VPD (Pa) + A2, A3: VPDthreshold (Pa) (below A3, gs = A1*VPDthreshold (Pa) + A2

! Farquhar's model parameters:
real, allocatable :: AVcmaxN(:,:) ! effect of leaf nitrogen on Vcmax at 25�C: Vcmax25� (�mol CO2 m-2 s-1) = A1*Na (g m-2) + A2
real, allocatable :: AJmaxN(:,:)  ! effect of leaf nitrogen on Jmax at 25�C: Jmax25� (�mol e m-2 s-1) = A1*Na (g m-2) + A2
real, allocatable :: ARdN(:,:)  ! effect of leaf nitrogen on dark respiration at 25�C: Rd25� (�mol CO2 m-2 s-1) = A1*Na (g m-2) + A2

! Mine parameters
integer, allocatable :: Ismine(:) ! =1 if vegetation type is mine, =0 if not
real, allocatable  :: epm(:)  ! product of leaf thickness * mine perimeter


contains
 subroutine vt_read(nent,pathVegetation,fnameVegetation)
!  Define the properties of vegetation types included in the 3D grid
!  This will include physical and physiological properties

! ALL VEGETATION TYPES ARE DEFINED IN A SINGLE RUN OF THE CREATE SUBROUTINE
! BUT DATA FOR EACH TYPE ARE IN A SEPARATE FILE

  integer :: nent  ! Number of vegetation types

  character*28 :: fnameVegetation  ! Name of file containing filenames for each vegetation type
  character*17 :: pathVegetation
  character*23, allocatable :: fname(:)  ! Input file name
  character*6 :: mfname
  integer :: jinc, jblo, jent
  real :: sumdistinc   ! Sum of % leaf area in leaf inclination class. Should be 1.

  call vt_destroy  ! deallocation des tableaux

  allocate(fname(nent))
  allocate(mu(nent))
  allocate(nbincli(nent))
  allocate(nblo(nent))

  pervoxel = .FALSE.

!  reading file <vegetationfname>, including file name for each vegetation type

  nblomin=100
  !vegetationfname='vegetation.'//spec
  open(2, file=fnameVegetation)
!  do while (.NOT. EOF(2))
!   read(2,*) jent, mfname
!   if ((jent.gt.0).and.(jent.le.nent)) then
!    fname(jent)=mfname
!    open(1,file=fname(jent))
!    read(1,*) mu(jent)
!    read(1,*) nbincli(jent)
!    nbinclimax=max(nbinclimax, nbincli(jent))
!    read(1,*)   ! skip 1 line in the file
!    read(1,*) nblo(jent)
!    nblomin=min(nblomin, nblo(jent))
!    close(1)
!   else
!   write(*,*) 'Vegetation type #',jent,' does not exist !'
!  end if
!  end do
  do while (.true.)
   read(2,*,end=999) jent, mfname
   if ((jent.gt.0).and.(jent.le.nent)) then
    fname(jent)=pathVegetation//mfname
    open(1,file=fname(jent))
    read(1,*,end=999) mu(jent)
    read(1,*,end=999) nbincli(jent)
    nbinclimax=max(nbinclimax, nbincli(jent))
    read(1,*,end=999)   ! skip 1 line in the file
    read(1,*,end=999) nblo(jent)
    nblomin=min(nblomin, nblo(jent))
    close(1)
   else
    !write(*,*) 'Vegetation type #',jent,' does not exist !'
   end if
  end do
  999 continue
  close(2)

  allocate(distinc(nent,nbinclimax))
  allocate(rf(nent,nblomin))

  allocate(Aga(nent,2))
  allocate(AgsN(nent,2),AgsPAR(nent,10),AgsCA(nent,10),AgsLT(nent,10),AgsVPD(nent,3))
  allocate(i_gsPAR(nent),i_gsCA(nent),i_gsLT(nent))

  allocate(AVCmaxN(nent,2))
  allocate(AJmaxN(nent,2))
  allocate(ARdN(nent,2))

  allocate(Ismine(nent))
  allocate(epm(nent))

  do jent=1,nent
   open (1,file=fname(jent))

!  1- Leaf inclination distribution
   read(1,*) ! skip 1 line (already read)
   read(1,*) ! skip 1 line (already read)
   read(1,*) (distinc(jent,jinc), jinc=1,nbincli(jent))

   sumdistinc=0.
   do jinc=1,nbincli(jent)
    sumdistinc=sumdistinc+distinc(jent,jinc)
   end do

!   write(*,*) '  Total % leaf area in inclination classes, for vegetation type # ',jent,': ',sumdistinc,'. SHOULD BE 1 '

!  2- Optical properties : average of leaf reflectance and transmittance
   read(1,*) ! skip 1 line
   read(1,*) (rf(jent,jblo), jblo=1,nblo(jent))

!  3- Parameters for leaf boundary conductance ga: ga = Aga(jent,1)* wind_speed + Aga(jent,2)
   read(1,*) Aga(jent,1), Aga(jent,2)


!  4- Jarvis'model parameters for stomatal conductance gs

!   effect of leaf nitrogen: gs (s m-1) = A1*Na (g m-2) + A2
   read(1,*) AgsN(jent,1), AgsN(jent,2)

!   effect of leaf PAR irradiance: gs (s m-1) = f(PAR, �mol m-2 s-1)
!   i_gsPAR=1: 2nd order polynomial : gs = A1*PAR�+A2*PAR+A3
   read(1,*) i_gsPAR(jent), nbparam, (AgsPAR(jent,i),i=1,nbparam)

!   effect of air CO2 partial pressure: gs (s m-1) = f(CA, Pa)
!   i_gsCA=1: 2nd order polynomial : gs = A1*CA�+A2*CA+A3
   read(1,*) i_gsCA(jent), nbparam, (AgsCA(jent,i),i=1,nbparam)

!   effect of leaf temperature: gs (s m-1) = f(LT, Pa)
!   i_gsLT=1: 2nd order polynomial : gs = A1*LT�+A2*LT+A3
   read(1,*) i_gsLT(jent), nbparam, (AgsLT(jent,i),i=1,nbparam)

!   effect of leaf VPD: gs (s m-1) = A1*VPD (Pa) + A2, A3: VPDthreshold (Pa) (below A3, gs = A1*VPDthreshold (Pa) + A2
   read(1,*) AgsVPD(jent,1), AgsVPD(jent,2), AgsVPD(jent,3)


!  5- Farquhar's model parameters:

!   effect of leaf nitrogen on Vcmax at 25�C: Vcmax25� (�mol CO2 m-2 s-1) = A1*Na (g m-2) + A2
   read(1,*) AVcmaxN(jent,1), AVcmaxN(jent,2)

!   effect of leaf nitrogen on Jmax at 25�C: Jmax25� (�mol e m-2 s-1) = A1*Na (g m-2) + A2
   read(1,*) AJmaxN(jent,1), AJmaxN(jent,2)

!   effect of leaf nitrogen on dark respiration at 25�C: Rd25� (�mol CO2 m-2 s-1) = A1*Na (g m-2) + A2
   read(1,*) ARdN(jent,1), ARdN(jent,2)

!  6- Mine parameters

   read(1,*,end=22) IsMine(jent) ! 1 if vegetation type #jent is a mine, 0 if not
   read(1,*) epm(jent)  ! product of leaf thickness * mine perimeter (in m�)
22   if (Ismine(jent).ne.1) then
    Ismine(jent)=0
    epm(jent)=1.
   endif

   close (1)
  end do

  if (allocated(fname))   deallocate(fname)

 end subroutine vt_read

 subroutine vt_destroy

  if (allocated(mu))   deallocate(mu)
  if (allocated(nbincli))  deallocate(nbincli)
  if (allocated(nblo))   deallocate(nblo)
  if (allocated(distinc))  deallocate(distinc)
  if (allocated(rf))   deallocate(rf)
  if (allocated(Aga))   deallocate(Aga)
  if (allocated(AgsN))   deallocate(AgsN)
  if (allocated(AgsPAR))  deallocate(AgsPAR)
  if (allocated(AgsCA))  deallocate(AgsCA)
  if (allocated(AgsLT))  deallocate(AgsLT)
  if (allocated(AgsVPD))  deallocate(AgsVPD)
  if (allocated(i_gsPAR))  deallocate(i_gsPAR)
  if (allocated(i_gsCA))  deallocate(i_gsCA)
  if (allocated(i_gsLT))  deallocate(i_gsLT)
  if (allocated(AVCmaxN))  deallocate(AVCmaxN)
  if (allocated(AJmaxN))  deallocate(AJmaxN)
  if (allocated(ARdN))   deallocate(ARdN)
  if (allocated(Ismine))  deallocate(Ismine)
  if (allocated(epm))   deallocate(epm)

 end subroutine vt_destroy

end module vegetation_types



!------------------------------------------------------------------------------
