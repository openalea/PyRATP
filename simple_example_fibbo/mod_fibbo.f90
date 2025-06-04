module fibbo
contains
  subroutine fib(a,n)
!
!     calculate first n fibonacci numbers
!
      integer :: n
      real, allocatable :: a(:)
      
      allocate(a(n))
      
      do i=1,n
         if (i.eq.1) then
            a(i) = 0.0
         elseif (i.eq.2) then
            a(i) = 1.0
         else 
            a(i) = a(i-1) + a(i-2)
         endif
      enddo
  end
end module fibbo
