module myprog

  use fibbo
  contains
  subroutine mysub
    real, allocatable :: a(:)
    
    call  fib(a,9)
    print*, a
  end subroutine mysub
  
end module myprog
