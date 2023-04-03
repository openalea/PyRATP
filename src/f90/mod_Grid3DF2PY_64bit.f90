!------------------------------------------------------------------------------

module grid3D

character*6	spec_grid		! for grid 3D definition
character*6	spec_gfill		! canopy structure for grid filling

!  EMPTY grid
integer :: njx, njy, njz    ! number of grid voxels along X Y and Z axis
real  :: dx, dy       ! voxel size according to X- and Y- axis
real, allocatable :: dz(:)    ! voxel size according to  Z- axis
real  :: xorig, yorig, zorig   ! 3D grid origin
real  :: latitude, longitude, timezone
real  :: orientation     ! angle (°) between axis X+ and North
integer :: idecaly                  ! offset between canopy units along Y-axis

! Soil surface
integer :: nsol       ! number of soil surface cells
integer :: nblosoil     ! Number of wavelength bands for the soil surface
real, allocatable    :: rs(:)      ! Soil reflectance in PAR and NIR bands
real :: total_ground_area   ! Total ground area of the scene


!   VEGETATED grid
integer(8) :: nveg       ! number of vegetated voxels
integer :: nent       ! number of vegetation types in the 3D grid
integer :: nemax       ! maximum number of vegetation types in a voxel (nemax < nent)

real, allocatable :: S_vt_vx(:,:) ! Leaf area (m²) per voxel and vegetation type
real, allocatable :: S_vx(:)       ! Leaf area (m²) per voxel
real, allocatable :: S_vt(:)    ! Leaf area (m²) per vegetation type
real ::      S_canopy        ! Leaf area (m²) of canopy (ex-variable sft)

real, allocatable :: volume_canopy(:)  ! cumulative volume (m3) of vegetated voxels, for each vegetation type, index nent+1 for total canopy volume
integer, allocatable :: voxel_canopy(:)  ! number of vegetated voxels, for each vegetation type
real :: N_canopy   ! average nitrogen content (g m-2)

integer, allocatable :: kxyz(:,:,:)  ! voxel index (as a function of location in the 3D grid)
integer, allocatable :: numx(:)   ! voxel x-coordinate (as a function of voxel #)
integer, allocatable :: numy(:)   ! voxel y-coordinate (as a function of voxel #)
integer, allocatable :: numz(:)   ! voxel z-coordinate (as a function of voxel #)
integer, allocatable :: nje(:)   ! number of vegetation types in voxel (as a function of voxel #)


integer, allocatable :: nume(:,:)   ! type # of each vegetation type in each voxel
real, allocatable    :: leafareadensity(:,:)   ! leaf area density of each vegetation type in each voxel
real, allocatable    :: N_detailed(:,:)   ! nitrogen content (g m-2) of each vegetation type in each voxel
integer :: int_scattering
integer :: int_isolated_box
logical :: scattering   ! TRUE if scattering variables must be computed
logical :: isolated_box   ! TRUE if isolated array of voxels (and FALSE if the array of voxels is surrounded with similar arrays, ie infinite canopy)

contains
 subroutine g3d_destroy
    if (allocated(dz))						deallocate(dz)
		if (allocated(kxyz))						deallocate(kxyz)
		if (allocated(numx))						deallocate(numx)
		if (allocated(numy))						deallocate(numy)
		if (allocated(numz))						deallocate(numz)
		if (allocated(nje))						deallocate(nje)
		if (allocated(leafareadensity))		deallocate(leafareadensity)
		if (allocated(N_detailed))				deallocate(N_detailed)
		if (allocated(nume))						deallocate(nume)

		if (allocated(S_vt_vx))					deallocate(S_vt_vx)
		if (allocated(S_vx))						deallocate(S_vx)
		if (allocated(S_vt))						deallocate(S_vt)
		if (allocated(volume_canopy))			deallocate(volume_canopy)


		if (allocated(rs))						deallocate(rs)

 end subroutine g3d_destroy
end module grid3D

!------------------------------------------------------------------------------
