!------------------------------------------------------------------------------

module constant_values

! Physical constants
real :: rho  ! air density (g m-3)
real :: lambda ! water vaporisation energy (J g-1)
real :: sigma  ! Stephan-Boltzman constant (W m-2 K-4)
real :: cp   ! heat capacity of the air (J g-1 K-1)
real :: gamma  ! psychrometric constant (Pa K-1) ?
real :: r   ! perfect gaz constant (?)

real :: pi   ! Number pi

contains

 subroutine cv_set

   rho=1184.
   lambda=2436.
   sigma=5.67e-8
   cp=1.01
   gamma=66.5
   r=8.3143

   pi=2.*acos(0.)

 end subroutine cv_set

end module constant_values

!------------------------------------------------------------------------------
