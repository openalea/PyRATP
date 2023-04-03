!------------------------------------------------------------------------------

module dir_interception

real  :: dpx, dpy      ! beam spacing along X- and Y- axis (m)

real, allocatable :: STAR_vt_vx(:,:)  ! STAR at voxel and vegetation type scale
real, allocatable :: STAR_vx(:)        ! STAR at voxel scale (ie, summing up on vegetation types included in the voxel)
real, allocatable :: STAR_vt(:)     ! STAR at vegetation type scale (ie, summing up on voxels)
real     :: STAR_canopy         ! STAR at canopy scale (ie, summing up on vegetation types and voxels)

real, allocatable :: S_detailed(:,:,:)        ! Shaded (i=0) and sunlit (i=1) leaf area of vegetation type jent, in voxel k (k=1,nveg)
real, allocatable :: S_ss_vt(:,:) ! Shaded (i=0) and sunlit (i=1) leaf area of vegetation type jent, i.e. summing up shaded or sunlit are on voxels
real              :: S_ss(0:1)      ! Shaded (i=0) and sunlit (i=1) leaf area in canopy, i.e. summing up shaded or sunlit are on voxels and vegetation types

real, allocatable :: share(:,:)  ! Sharing coeff of intercepted radiation in voxel k (k=1,nveg), for the studied direction
real, allocatable :: xk(:)   ! Optical density of voxel k (k=1,nveg), = somme(Ki*LADi)
real, allocatable :: rka(:)  ! Fraction of scattered radiation in current direction by vegetation type jent (jent=1,nent)
real, allocatable :: rkavox(:,:)  ! Fraction of scattered radiation in current direction by vegetation type jent (jent=1,nent) and for each voxel
real, allocatable :: riv(:)  ! fraction of directional incident radiation intercepted in voxel k (k=1,nveg)
real, allocatable :: rtv(:)  ! fraction of directional incident radiation transmitted in voxel k (k=1,nveg)
real, allocatable :: ris(:)  ! fraction of directional incident radiation intercepted by ground zone ksol (ksol=1,nsol)
real, allocatable :: ffvvb(:,:) ! Exchange coeff between vegetated voxels and vegetated voxels
real, allocatable :: ffsvb(:,:) ! Exchange coeff between vegetated voxels and soil surface
real, allocatable :: ffcvb(:)  ! Exchange coeff between vegetated voxels and sky
real, allocatable :: ffvsb(:,:) ! Exchange coeff between soil surface and vegetated voxels
real, allocatable :: ffcsb(:)  ! Exchange coeff between soil surface and sky


!logical :: isolated_box   ! TRUE if isolated array of voxels (and FALSE if the array of voxels is surrounded with similar arrays, ie infinite canopy)


contains
 subroutine di_doall(hmoy0, azmoy0, omega0, dpx0, dpy0, scatt0, ib0)


!
! Compute directional interception, i.e. variables ri, ff__b,
!   for a given direction, i.e. defined by direction (hmoy0,azmoy0) (in degree) and solide angle omega0
!   works for either diffuse and direct radiation

 use constant_values     ! For number pi
 use grid3D
 use vegetation_types

 real :: hmoy0, azmoy0, omega0  ! scalars in module dir_interception
 real :: dpx0, dpy0     ! Beam spacing along X- and Y-axis, as entered when calling subroutine
 logical :: scatt0      ! .TRUE. if exchange coefficients for scattered radiation must be computed
 logical :: ib0       ! .TRUE. if the array of voxels is an isolated box, i.e. not surrounded with similar boxes
 integer ::idmx, idmy     ! Number of beams sent per voxel top along X-axis, and Y-axis
 real :: di, xic, xm, G_function, sumrka
 integer :: k, jdir, je, jent

 real :: oax, oay, oaz    ! direction cosines
 real :: x0, y0, z0     ! co-ordinates of entering point in voxel
 integer :: jx,jy,jz     ! voxel indices along X- Y- and Z- axes

 real, allocatable :: xka(:)
 real, allocatable :: xkavox(:,:) ! for each voxel and each entity

  ! write(*,*) 'di_doall debut', hmoy0,azmoy0

  hmoy0=hmoy0*pi/180.    ! Conversion to radians
  azmoy0=azmoy0*pi/180.

  dpx=dpx0
  dpy=dpy0
  idmx = int((dx/dpx)+0.5)  ! Number of beams sent along X-axis
  dpx=dx/real(idmx)     ! Correcting dpx, to get an non-fractional number of beams
  idmy = int((dy/dpy)+0.5)  ! Number of beams sent along Y-axis
  dpy=dy/real(idmy)     ! Correcting dpy, to get an non-fractional number of beams

  scattering=scatt0
  isolated_box=ib0

  call di_destroy

! Part 1: Extinction coefficients for each cell,
!         Scattered radiation fields for each vegetation type within cells
!         Sharing coefficients between vegetation type within cells

!  write(*,*)
!  write(*,*) 'Part #: Directional extinction and scattering'
!  write(*,*) '        coefficients (for each voxel)'

! Calcul des coefficients d'extinction et du champ de rayonnement
! rediffuse pour chaque composante de v�g�tation : xka(jent)
!                                                 rka(jent)
! (hypothese de distribution uniforme des azimuths)
! (hypothese de comportement lambertien des feuilles)
  
!  write(*,*) 'nbincli',nbincli,'nent',nent
  if (.NOT. pervoxel) then 
    allocate(xka(nent))
    allocate(rka(nent)) 
    xka=0.
    rka=0.
    do jent=1,nent  ! For each vegetation type
  !   sumrka=0.  ! Sum of rka over directions should be ONE
      di=(pi/2.)/nbincli(jent)
      do jinc=1,nbincli(jent)
        xic=(real(jinc)-.5)*di
        if (xic.le.hmoy0) then
          G_function=cos(xic)*sin(hmoy0)
        else
          xm=acos(-tan(hmoy0)/tan(xic))
          G_function=(2*cos(hmoy0)*sin(xic)*sin(xm)-cos(xic)*sin(hmoy0)*(pi-2*xm))/pi
        endif
        !    pause
        xka(jent)=xka(jent) + G_function/sin(hmoy0) * distinc(jent,jinc)
        rka(jent)=rka(jent) + G_function*omega0/(2.*pi) * distinc(jent,jinc)

! rem: rka est une variable qui peut �tre utilis�e � l'�chelle des voxels
!   puisque qu'elle int�gre la convolution avec la distribution d'inclinaison
!   La variable rk (incluse dans les versions pr�c�dentes de RIRI et RATP) n'est donc plus utile
!
! rem: ATTENTION � v�rifier que sumrka devrait �tre 1 ou 0.5 !!!
    end do
!    sumrka=sumrka+rka(jent,jdir)
!   write(*,*) 'Direction-integrated scattered radiation by vegetation type #',jent,': ',sumrka,' . SHOULD BE ONE'
  end do   ! next vegetation type

! cadre d'une distribution d'angle par voxel
else 
  allocate(xkavox(nveg, nent))
  allocate(rkavox(nveg, nent))
  xkavox=0.
  rkavox=0.
  do kt=1,nveg ! For each voxel
    do jent=1,nje(kt)  ! For each vegetation type in a voxel
  !   sumrka=0.  ! Sum of rka over directions should be ONE
      di=(pi/2.)/nbinclivox
      do jinc=1,nbinclivox ! for each elevation class
        xic=(real(jinc)-.5)*di
        if (xic.le.hmoy0) then
          G_function=cos(xic)*sin(hmoy0)
        else
          xm=acos(-tan(hmoy0)/tan(xic))
          G_function=(2*cos(hmoy0)*sin(xic)*sin(xm)-cos(xic)*sin(hmoy0)*(pi-2*xm))/pi
        endif
        !    write(*,*) xic*180./pi, hmoy0*180./pi, G_function/sin(hmoy0)
        !    pause
        xkavox(kt, jent)=xkavox(kt, jent) + G_function/sin(hmoy0) * distincvox(kt, jent, jinc)
        rkavox(kt, jent)=rkavox(kt, jent) + G_function*omega0/(2.*pi) * distincvox(kt, jent, jinc)
      end do
    end do
  end do
endif

! do je=1,nent
!   write(*,*) "xka", xka(je)
! end do

! Calcul des coeff d'extinction de chaque voxel k: x
  
! k(k), pour chaque direction k
!        du partage du rayonnement entre composantes: share(je,k)
  
     
  allocate(xk(0:nveg))
  allocate(share(nemax,nveg))
  xk=0.
  share=0.
  do k=1,nveg
    do je=1,nje(k)
      if (.NOT. pervoxel) then
        share(je,k) = xka(nume(je,k)) * leafareadensity(je,k) *mu(nume(je,k))  ! Inclusion of a leaf dispersion parameter   (done on 11 March 2008)
        ! write(*,*) "lad",k,je,leafareadensity(je,k)
      else
        share(je,k) = xkavox(k, je) * leafareadensity(je,k) *mu(nume(je,k))  ! Inclusion of a leaf dispersion parameter per voxel   (done on 06 April 2022)
      endif
      xk(k) = xk(k) + share(je,k)  ! optical density = sum(Kje*LADje)
       
    end do
    do je=1,nje(k)
      share(je,k) = share(je,k) / xk(k) ! sharing coefficient
      ! write(*,*)"xk",k,xk(k)
    end do
  end do

!  write(*,*) 'deallocate(xka)'
  if (.NOT. pervoxel) then
    deallocate(xka)  ! Not ever used
  else
    deallocate(xkavox)
  endif


! Part 2: Diffuse and scattered radiation interception:
!                Diffuse radiation: Exchange coefficients between the sky and the vegetation (and soil) voxels.
!                Scattered radiation: Exchange coefficients between vegetation (and soil) voxels.


!  write(*,*)
!  write(*,*) 'Part #: Diffuse and scattered radiation interception'

!  Allocation et Initialisation des tableaux de STAR et facteurs de forme

!  1- STAR at different scales
  allocate(STAR_vt_vx(nemax,nveg))  ! STAR at voxel and vegetation type scale
  allocate(STAR_vx(nveg))     ! STAR at voxel and vegetation type scale
  allocate(STAR_vt(nent))     ! STAR at voxel and vegetation type scale
  STAR_vt_vx = 0.
  STAR_vx = 0.
  STAR_vt = 0.
  STAR_canopy = 0.   

!  2- Facteurs de forme pour le rayonnement incident

  allocate(riv(0:nveg))
  allocate(rtv(0:nveg))
  allocate(ris(nsol))
  riv=0.
  rtv=0.
  ris=0.

!  3- Facteurs de forme pour le rayonnement rediffuse
!             Source = vegetation voxels

  if (scattering) then        ! allocation of exchange coeff arrays only if scattering must be computed 
   allocate(ffvvb(0:nveg,0:nveg)) ! Exchange coeff between vegetated voxels and vegetated voxels 
   allocate(ffsvb(nsol,0:nveg))  ! Exchange coeff between vegetated voxels and soil surface
   allocate(ffcvb(0:nveg))    ! Exchange coeff between vegetated voxels and sky
   ffvvb=0.
   ffsvb=0.
   ffcvb=0.
!             Source = soil surface areas 
   allocate(ffvsb(0:nveg,nsol))  ! Exchange coeff between soil surface and vegetated voxels
   allocate(ffcsb(nsol))    ! Exchange coeff between soil surface and sky
   ffvsb=0.
   ffcsb=0.
  end if

!     For the given direction given by scalars hmoy0, azmoy0, omega0

  oay = cos(hmoy0)*sin(azmoy0)
  oax = cos(hmoy0)*cos(azmoy0)
  oaz = sin(hmoy0)
!     Rem: Le choix des cosinus directeurs implique que:
!             X > 0 : Axe dirig� vers le Nord (ou Direction des rangs)
!             Y > 0 : Axe dirig� vers l'Est
!     Rem1: Ne pas oublier qu'un rayon venant du Sud-Ouest
!                                avance vers le Nord-Est
!     Rem2: Les definitions de oax et oay sont inversees par rapport
!             aux versions precedentes de RIRI3D, ceci pour etre conforme
!             aux axes X et Y definis dans le fichier shootlad.<spec>
  if (oax.eq.0.) oax=1.e-08
  if (oay.eq.0.) oay=1.e-08
  if (oaz.eq.0.) oaz=1.e-08

!  write(*,*) 'Azimuth:',azmoy0*180./pi,' Elevation:',hmoy0*180./pi

!  Beam sampling
  do idx=1, idmx
  do idy=1, idmy
   x0 = (real(idx)-.5)*dpx
   y0 = (real(idy)-.5)*dpy
   z0 = 0.
   call beampath(oax, oay, oaz, x0, y0, z0, omega0)
  end do
  end do
! STAR computations (from coefficients riv and share, and dividing by leaf area)

 ! write(*,*) 'STAR computations'
  do k=1,nveg
   do je=1, nje(k)
    jent=nume(je,k)
    STAR_vt_vx(je,k) = riv(k)*share(je,k)*oaz
    STAR_vx(k)=STAR_vx(k)+STAR_vt_vx(je,k)
    STAR_vt(jent)=STAR_vt(jent)+STAR_vt_vx(je,k)
    STAR_vt_vx(je,k)=STAR_vt_vx(je,k)/S_vt_vx(je,k)
   end do
   STAR_vx(k)=STAR_vx(k)/S_vx(k)
  end do

  do jent=1,nent
   STAR_canopy = STAR_canopy + STAR_vt(jent)
   STAR_vt(jent)=STAR_vt(jent)/S_vt(jent)
  end do

  STAR_canopy = STAR_canopy / S_canopy

!
!  Sunlit and shaded area of each vegetation type in each voxel:
!  S_detailed(0,je,k) : shaded leaf area (m�) of vegetation type je in voxel k
!  S_detailed(1,je,k) : sunlit leaf area (m�) of vegetation type je in voxel k
!  NOTE:  Due to random leaf dispersion within voxel,
!     the fraction of sunlit area is the same for all vegetation types included in the voxel
                         
!  write(*,*) ' ... allocate S_detailed ... '
  allocate(S_detailed(0:1,nemax,nveg)) ! Shaded/sunlit area per vegetation type and voxel
  allocate(S_ss_vt(0:1,nent))    ! Shaded/sunlit area per vegetation type
  S_ss_vt=0.
  S_ss=0.
!  write(*,*) ' ... allocate S_detailed OK '
  
  do k=1,nveg
  do je=1,nje(k)
   S_detailed(1,je,k)=amax1((riv(k)/xk(k))*leafareadensity(je,k),1.e-08)
   ! CF 2016: I would have expected S_detailed(1,je,k) = riv(k) * share(je,k)
   S_detailed(0,je,k)=S_vt_vx(je,k)-S_detailed(1,je,k)
   jent=nume(je,k)
   do joe=0,1
    S_ss_vt(joe,jent)=S_ss_vt(joe,jent)+S_detailed(joe,je,k)
    S_ss(joe)=S_ss(joe)+S_detailed(joe,je,k)
   end do
  end do
  end do

!  write(*,*) 'STAR_canopy=', STAR_canopy
!  write(*,*) 'Sunlit / total leaf area at canopy scale: ', S_ss(1)/S_canopy

  hmoy0=hmoy0/pi*180.    ! Conversion to degrees
  azmoy0=azmoy0/pi*180.

 end subroutine di_doall

 subroutine beampath(oax, oay, oaz, x0, y0, z0, omega0)
!
! Suivi du chemin et de l'extinction des rayons elementaires
! au cours de leur traversee dans le couvert.

 use constant_values     ! For number pi
 use grid3D
 use vegetation_types

 parameter (nraymax=2000)

 real :: p0(nraymax),p(nraymax),pini(nraymax)
 real :: sortdelascene(nraymax)    ! 1 if the beam enters the scene, 0 if not
 real :: downlayer(nraymax)    ! 1 if the beam downs one layer, 0 if not
 real :: dzp(nraymax)
 integer :: num(nraymax),jxnum(nraymax),jynum(nraymax),jznum(nraymax)

 real :: xlx, xly, xlz, x1, y1, z1
 real :: dzz, r0, r0c, r00v, r0s

 real :: oax, oay, oaz    ! direction cosines
 real :: x0, y0, z0     ! co-ordinates of entering point in voxel
 integer :: jx,jy,jz     ! voxel indices along X- Y- and Z- axes
 real :: omega0       ! solid angle associated to beam direction


! Calcul des:
!  Fractions de rayonnement incident intercept�es
!  Facteurs de forme entre diffuseurs et recepteurs: ff<recepteur><source>

! Step 1: Beam - voxels intersection
!  Identifying the sequence of voxels crossed by the beam : num
!  Vegetation thickness in each visited voxel : dzp

  jx=1  ! Beam - voxel intersection geometry is computed from beams entering the canopy in the top side of voxel(1,1,1)
  jy=1  ! Beam - voxel intersection for other voxels at the top of the canopy is computed from translation relationships, in the second part of subroutine beampath
  jz=1

  jvx=jx
  jvy=jy
  kt=1
  dzz=dz(1)
  jxnum(1)=jx
  jynum(1)=jy
  jznum(1)=jz

  sortdelascene=0.
  downlayer=0.

  do while (jz.lt.njz+1)  ! while the beam does not reach the soil surface
    nx=jvx+int((sign(1.,oax)-1.)/2.)
    ny=jvy+int((sign(1.,oay)-1.)/2.)
    xlx= abs((real(nx)*dx-x0)/oax)
    xly= abs((real(ny)*dy-y0)/oay)
    xlz= abs((dzz-z0)/oaz)
    xlt=amin1(xlx,xly,xlz)
    x1=x0+xlt*oax     ! co-ordinates of the beam output point
    y1=y0+xlt*oay
    z1=z0+xlt*oaz
    dzp(kt)=z1-z0     ! foliage thickness crossed by the beam in voxel kt

    if (xlt.eq.xlx) then      ! voxel indices of next visited voxel
      jvx=jvx+int(sign(1.,oax))
      jx=jx+int(sign(1.,oax))
      downlayer(kt) = 0
    endif
    if (xlt.eq.xly) then
      jvy=jvy+int(sign(1.,oay))
      jy=jy+int(sign(1.,oay))
      downlayer(kt) = 0
    endif
    if (xlt.eq.xlz) then
      jz=jz+1
      dzz=dzz+dz(jz)
      ! if we down one layer
      downlayer(kt) = 1
    endif
    x0=x1
    y0=y1
    z0=z1

    !   Normalising voxel indices in case of beam output from the 3D grid
    !   The scene is assumed infinite, ie the beam enters the 3D grid from the opposite side

    if (jx.gt.njx) then
      jx=jx-njx
      jy=jy-idecaly
      !    Decalage de jy si les mailles ne sont pas alignees (quinconce)
      if (isolated_box) then
        !sortdelascene(kt)=abs(1.*isolated_box)  ! Rem:  .TRUE.=-1 and .FALSE.=0
        sortdelascene(kt)=1
      else
        sortdelascene(kt)=0
      endif
    endif
    if (jx.lt.1) then
      jx=jx+njx
      jy=jy-idecaly
      !    Decalage de jy si les mailles ne sont pas alignees (quinconce)
      if (isolated_box) then
        !sortdelascene(kt)=abs(1.*isolated_box)  ! Rem:  .TRUE.=-1 and .FALSE.=0
        sortdelascene(kt)=1
      else
        sortdelascene(kt)=0
      endif
    endif
    if (jy.gt.njy) then
      jy=jy-njy
      if (isolated_box) then
        !sortdelascene(kt)=abs(1.*isolated_box)  ! Rem:  .TRUE.=-1 and .FALSE.=0
        sortdelascene(kt)=1
      else
        sortdelascene(kt)=0
      endif
    endif
    if (jy.lt.1) then
      jy=jy+njy
      if (isolated_box) then
        !sortdelascene(kt)=abs(1.*isolated_box)  ! Rem:  .TRUE.=-1 and .FALSE.=0
        sortdelascene(kt)=1
      else
        sortdelascene(kt)=0
      endif
    endif

    ! write(*,*) 'kt=',kt,'jx=',jx,'jy=',jy,'jz=',jz

    kt=kt+1
    if (kt.gt.nraymax) then
      !write(*,*) 'Fin intempestive dans Beampath'
      !write(*,*) 'Too much voxels crossed by the beam (>',nraymax,')'
      return
    endif

    jxnum(kt)=jx
    jynum(kt)=jy
    jznum(kt)=jz
  end do ! (while (jz.lt.njz+1)

  ktm=kt
!  write(*,*) 'Nombre de cellules traversees :',kt-1


!  Step 2 :
!  Computing beam contribution to exchange coefficients
!
  r0c = dpx*dpy
  r00v=(dpx*dpy)/(dx*dy)
!  r0s=(dpx*dpy)/(dx*dy)*omega0/(2.*pi)
  r0s=(dpx*dpy)/(dx*dy)*oaz*omega0/pi
  do jxx=1,njx
    do jyy=1,njy
      do kt=1,ktm   ! Storing voxel id. in variable num(kt)
        jz=jznum(kt)
        jx=jxnum(kt)+jxx-1
        if (jx.gt.njx) jx=jx-njx
        jy=jynum(kt)+jyy-1
        if (jy.gt.njy) jy=jy-njy
        ! write(*,*) 'jx,jy,jz,num(kt)=kxyz(jx,jy,jz) :',jx,jy,jz,kxyz(jx,jy,jz)
        num(kt)=kxyz(jx,jy,jz)
      end do  ! do-loop KT=1,KTM
      do kt=1,ktm-1      ! Computing light interception properties of grid voxels
        ft=xk(num(kt))*dzp(kt)
        p0(kt)=exp(-ft)
        p(kt)=1.-p0(kt)
        ! write(*,*)"xk",xk(num(kt)),"dz",dzp(kt),"p0",p0(kt),"1-p0",p(kt)
        if (ft.ne.0.) then
          pini(kt)=p(kt)/ft
        else
          pini(kt)=0.
        endif
        !write(*,*)"pini",pini(kt),num(kt)
      end do  ! do-loop KT=1,KTM-1
!
!     1- Facteurs de forme entre ciel et tubes
!
      r0=r0c
      do kt=1,ktm-1
        riv(num(kt))=riv(num(kt))+r0*p(kt)
        ! transmitted light downwise direction
        rtv(num(kt))=rtv(num(kt))+r0*p0(kt)*downlayer(kt)
        ! write(*,*) "riv",kt,num(kt), riv(num(kt)),rtv(num(kt))
        r0=amax1(r0*p0(kt),sortdelascene(kt)*r0c)
      end do
      ris(num(ktm))=ris(num(ktm))+r0

      if (scattering) then

!
!     2- Facteurs de forme entre vegetated voxels et le reste
!
        do kts=1,ktm-1  ! For each voxel along the beam, as a potential source of scattered radiation
        ks=num(kts)

        if (ks.gt.0) then

          r00=r00v*dzp(kts)/dz(numz(ks))
          ffvvb(ks,ks)=ffvvb(ks,ks) + r00 * 2.*(1-pini(kts))

    !      Downward flux

          r0=pini(kts)*r00
          if (kts.ne.ktm-1) then
          do ktr=kts+1,ktm-1
            ffvvb(num(ktr),ks)=ffvvb(num(ktr),ks) + r0 * p(ktr)
            r0=r0*p0(ktr)
          end do
          endif
          ffsvb(num(ktm),ks)=ffsvb(num(ktm),ks) + r0

    !      Upward flux

          r0=pini(kts)*r00
          if (kts.ne.1) then
          do ktr=kts-1,1,-1
            ffvvb(num(ktr),ks)=ffvvb(num(ktr),ks) + r0 * p(ktr)
            r0=r0*p0(ktr)
          end do
          endif
          ffcvb(ks)=ffcvb(ks) + r0

        endif  ! if (ks.gt.0)

        end do  ! do kts=1,ktm-1


!
!     3- Facteurs de forme entre le sol et le reste
!
    r0=r0s
    ks=num(ktm)
    do ktr=ktm-1,1,-1
     ffvsb(num(ktr),ks)=ffvsb(num(ktr),ks) + r0 * p(ktr)
     r0=r0*p0(ktr)
    end do
    ffcsb(ks)=ffcsb(ks) + r0

  endif   ! if (scattering)

  end do  ! do-loop JYY
  end do  ! do-loop JXX

 end subroutine beampath

 subroutine di_destroy

  if (allocated(rka))   deallocate(rka)
  if (allocated(rkavox))   deallocate(rkavox)
  if (allocated(xk))   deallocate(xk)
  if (allocated(share))  deallocate(share)

  if (allocated(STAR_vt_vx)) deallocate(STAR_vt_vx) ! STAR at voxel and vegetation type scale
  if (allocated(STAR_vx))  deallocate(STAR_vx)  ! STAR at voxel and vegetation type scale
  if (allocated(STAR_vt))  deallocate(STAR_vt)  ! STAR at voxel and vegetation type scale

  if (allocated(riv))   deallocate(riv)
  if (allocated(rtv))   deallocate(rtv)
  if (allocated(ris))   deallocate(ris)

  if (allocated(ffvvb))  deallocate(ffvvb)  ! Exchange coeff between vegetated voxels and vegetated voxels
  if (allocated(ffsvb))  deallocate(ffsvb)  ! Exchange coeff between vegetated voxels and soil surface
  if (allocated(ffcvb))  deallocate(ffcvb)  ! Exchange coeff between vegetated voxels and sky
  if (allocated(ffvsb))  deallocate(ffvsb)  ! Exchange coeff between soil surface and vegetated voxels
  if (allocated(ffcsb))  deallocate(ffcsb)  ! Exchange coeff between soil surface and sky

  if (allocated(S_detailed)) deallocate(S_detailed)
  if (allocated(S_ss_vt))  deallocate(S_ss_vt)

 end subroutine di_destroy

end module dir_interception


!------------------------------------------------------------------------------
