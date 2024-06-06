!------------------------------------------------------------------------------

module hemi_interception

real, allocatable :: STARsky_vt_vx(:,:)  ! Sky-integrated STAR at voxel and vegetation type scale
real, allocatable :: STARsky_vx(:)        ! Sky-integrated STAR at voxel scale (ie, summing up on vegetation types included in the voxel)
real, allocatable :: STARsky_vt(:)     ! Sky-integrated STAR at vegetation type scale (ie, summing up on voxels)
real ::      STARsky_canopy         ! Sky-integrated STAR at canopy scale (ie, summing up on vegetation types and voxels)

real, allocatable :: rdiv(:,:)  ! Fraction of incident diffuse radiation intercepted by voxel k, k=1,nveg
real, allocatable :: rdtv(:,:)  ! Fraction of incident diffuse radiation transmitted by voxel k, k=1,nveg
real, allocatable :: rdis(:)   ! Fraction of incident diffuse radiation intercepted by ground_zone ksol, ksol=1,nsol

real, allocatable :: ffvv(:,:,:,:) ! Exchange coeff between vegetation type js in voxel ks and vegetation type jr in voxel jr
real, allocatable :: ffsv(:,:,:)  ! Exchange coeff between vegetation type js in voxel ks and ground_zone ksol
real, allocatable :: ffcv(:,:)  ! Exchange coeff between vegetation type js in voxel ks and sky (i.e. for reflected radiation)
real, allocatable :: ffvs(:,:,:)  ! Exchange coeff between ground_zone ksol and vegetation type js in voxel ks
real, allocatable :: ffcs(:)   ! Exchange coeff between ground_zone ksol and sky (i.e. for reflected radiation)

contains

 subroutine hi_doall(dpx0,dpy0,ib0)

 use constant_values     ! For number pi
 use grid3D
 use skyvault
 use vegetation_types
 use dir_interception

 real :: aa, at, rtot
 real :: dpx0, dpy0
 logical :: ib0    ! TRUE if isolated box
 integer :: AllocateStatus


  scattering=.TRUE.
  isolated_box=ib0

!
!  Allocation et initialisation des tableaux de facteurs de forme
  call hi_destroy
!
!  1- Sky_integrated STAR at different scales
                                       
  allocate(STARsky_vt_vx(nemax,nveg))
  allocate(STARsky_vx(nveg))
  allocate(STARsky_vt(nent))
  STARsky_vt_vx = 0.
  STARsky_vx = 0.
  STARsky_vt = 0.
  STARsky_canopy = 0.  

!  2- Facteurs de forme pour le rayonnement diffus incident
                                                       
  allocate(rdiv(nemax,nveg))
  allocate(rdtv(nemax,nveg))
  allocate(rdis(nsol))
  rdiv=0.
  rdtv=0.
  rdis=0.       

!  3- Facteurs de forme pour le rayonnement rediffuse
!             Source = vegetation
  allocate(ffvv(nveg,nemax,nveg,nemax),stat=AllocateStatus)
  if (AllocateStatus /= 0) stop "*** Sorry, Not enough memory for allocating ffvv table***"
  allocate(ffsv(nsol,nveg,nemax))
  allocate(ffcv(nveg,nemax))
!  ffsv=0.
!  ffcv=0.
!  ffvv=0.
!             Source = surface du sol
  allocate(ffvs(nveg,nemax,nsol))
  allocate(ffcs(nsol))
!  ffvs=0.
!  ffcs=0.

!  Array initialisation
  do ks=1,nveg   ! source = vegetated voxels
    do kr=1,nveg
      do jes=1,nje(ks)  ! receptor = vegetated voxels
        do jer=1,nje(kr)
          ffvv(kr,jer,ks,jes)=0.
        end do
      end do
    end do
    do kr=1,nsol    ! receptor = ground zones
      do jes=1,nje(ks)
        ffsv(kr,ks,jes)=0.
      end do
    end do
    do jes=1,nje(ks)
      ffcv(ks,jes)=0.  ! receptor = sky (i.e. reflected radiation)
    end do
  end do  ! do-loop ks=1,nveg (source = vegetated voxels)  
  do ks=1,nsol   ! source = ground zones
    do kr=1,nveg    ! receptor = vegetated voxels
      do jer=1,nje(kr)
        ffvs(kr,jer,ks)=0.
      end do
    end do
    ffcs(ks)=0. ! receptor = sky
  end do   ! End of array initialisation


!     For each sky direction jdir, jdir=1,ndir
    ! write(*,*) 'ndir',ndir

!   Directional interception (includes computation of extinction coefficient, beam sampling, and exchange coefficients)
  do jdir=1,ndir
!  write(*,*) 'jdir',jdir
!  write(*,*) 'DEBUG: ARGS',hmoy(jdir)*180./pi 
!  write(*,*) 'DEBUG: ARGS', azmoy(jdir)*180./pi 
!  write(*,*) 'DEBUG: ARGS', omega(jdir),dpx0,dpy0,scattering,isolated_box
  
    call di_doall(hmoy(jdir)*180./pi, azmoy(jdir)*180./pi, omega(jdir),dpx0,dpy0,scattering,isolated_box) 

!   Sky-vault integration of incident diffuse radiation interception
    do k=1,nveg
      aa = pc(jdir) * riv(k)
      at = pc(jdir) * rtv(k)
      do je=1,nje(k)
        rdiv(je,k) = rdiv(je,k) + aa * share(je,k)
        rdtv(je,k) = rdtv(je,k) + at * share(je,k)
        ! write(*,*)"inter",k,je,rdiv(je,k),rdtv(je,k),aa,pc(jdir),riv(k),rtv(k)
      end do
    end do
    do k=1,nsol
        rdis(k) = rdis(k) + pc(jdir) * ris(k)
    end do

!   STAR computations (from coefficients riv and share)

    do k=1,nveg
      do je=1, nje(k)
        jent=nume(je,k)
        STARsky_vt_vx(je,k) = STARsky_vt_vx(je,k) + riv(k)*share(je,k)* pc(jdir)
        !  write(*,*)"rdtv",k,je,rdtv(je,k)
      end do
    end do

    !   Sky-vault integration of scattered radiation interception
    do ks=1,nveg   ! source = vegetated voxels
      do kr=1,nveg
        do jes=1,nje(ks)  ! receptor = vegetated voxels
          do jer=1,nje(kr)
            if (.NOT. pervoxel) then  
              ffvv(kr,jer,ks,jes)=ffvv(kr,jer,ks,jes)+ rka(nume(jes,ks))*ffvvb(kr,ks)*share(jer,kr)
            else
              ffvv(kr,jer,ks,jes)=ffvv(kr,jer,ks,jes)+ rkavox(ks,jes)*ffvvb(kr,ks)*share(jer,kr)
            endif
          end do
        end do
      end do
      do kr=1,nsol    ! receptor = ground zones
        do jes=1,nje(ks)
          if (.NOT. pervoxel) then  
            ffsv(kr,ks,jes)=ffsv(kr,ks,jes)+ rka(nume(jes,ks))*ffsvb(kr,ks)
          else
            ffsv(kr,ks,jes)=ffsv(kr,ks,jes)+ rkavox(ks,jes)*ffsvb(kr,ks)
          endif
        end do
      end do
      do jes=1,nje(ks)
        if (.NOT. pervoxel) then  
          ffcv(ks,jes)=ffcv(ks,jes)+rka(nume(jes,ks))*ffcvb(ks)  ! receptor = sky (i.e. reflected radiation)
        else
          ffcv(ks,jes)=ffcv(ks,jes)+rkavox(ks,jes)*ffcvb(ks)  ! receptor = sky (i.e. reflected radiation)
        endif
      end do
    end do  ! do-loop ks=1,nveg (source = vegetated voxels)

         do ks=1,nsol   ! source = ground zones
            do kr=1,nveg    ! receptor = vegetated voxels
               do jer=1,nje(kr)
                  ffvs(kr,jer,ks)=ffvs(kr,jer,ks)+ ffvsb(kr,ks)*share(jer,kr)
     end do
    end do
            ffcs(ks)=ffcs(ks)+ffcsb(ks) ! receptor = sky
   end do

  end do

! STAR computations (from coefficients riv and share, and dividing by leaf area)

  do k=1,nveg
   do je=1, nje(k)
    jent=nume(je,k)
    STARsky_vx(k)=STARsky_vx(k)+STARsky_vt_vx(je,k)
    STARsky_vt(jent)=STARsky_vt(jent)+STARsky_vt_vx(je,k)
    STARsky_vt_vx(je,k)=STARsky_vt_vx(je,k)/S_vt_vx(je,k)
   end do
   STARsky_vx(k)=STARsky_vx(k)/S_vx(k)
  end do

  do jent=1,nent
   STARsky_canopy = STARsky_canopy + STARsky_vt(jent)
   STARsky_vt(jent)=STARsky_vt(jent)/S_vt(jent)
  end do

  STARsky_canopy = STARsky_canopy / S_canopy
  ! write(*,*) 'STARsky_canopy =', STARsky_canopy
  ! write(*,*) 'S_canopy =', S_canopy


! Verification de la conservation des rayonnements

     rtot=0.
  do k=1, nveg
  do je=1,nje(k)
         rtot = rtot +rdiv(je,k)
  end do
  end do
  do k=1,nsol
   rtot = rtot +rdis(k)
  end do
  rtot=rtot/(float(njx)*dx*float(njy)*dy)
!  write(*,*) '  Total diffuse intercepted radiation: ',rtot,' SHOULD BE 1'

  rtot=0.
  do ks=1,nsol
   rtot=rtot+ffcs(ks)
   do kr=1,nveg
   do jer=1,nje(kr)
    rtot=rtot+ffvs(kr,jer,ks)
   end do
   end do
  end do

    ! write(*,*)'Total scattered radiation by the ground: ',rtot/njx/njy,' SHOULD BE 1'
  do ks=1,nveg
  do jes=1,nje(ks)
   rtot=0.
   rtot=rtot+ffcv(ks,jes)
   do kr=1,nveg
   do jer=1,nje(kr)
    rtot=rtot+ffvv(kr,jer,ks,jes)
   end do
   end do
   do kr=1,nsol
    rtot=rtot+ffsv(kr,ks,jes)
   end do
  ! write(*,*)'Total scattered radiation by vegetation type ',jes,' in voxel ',ks, ': ',rtot,' SHOULD BE 1'
  end do
  end do

 end subroutine hi_doall

 subroutine hi_destroy

  if (allocated(STARsky_vt_vx)) deallocate(STARsky_vt_vx)
  if (allocated(STARsky_vx))  deallocate(STARsky_vx)
  if (allocated(STARsky_vt))  deallocate(STARsky_vt)

  if (allocated(rdiv)) deallocate(rdiv)
  if (allocated(rdtv)) deallocate(rdtv)
  if (allocated(rdis)) deallocate(rdis)

  if (allocated(ffvv)) deallocate(ffvv)
  if (allocated(ffsv)) deallocate(ffsv)
  if (allocated(ffcv)) deallocate(ffcv)
  if (allocated(ffvs)) deallocate(ffvs)
  if (allocated(ffcs)) deallocate(ffcs)

 end subroutine hi_destroy


end module hemi_interception

!------------------------------------------------------------------------------
