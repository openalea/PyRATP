#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ngao
#
# Created:     10/01/2014
# Copyright:   (c) ngao 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    import pyratp
    grid = pyratp.grid3d
    grid.dx=3
    gridmat={}
    gridmat['dx']=2
    i = 'dx'
    exec('print grid.'+i)

    exec('grid.'+i+'=gridmat["'+i+'"]')
    print(grid.dx)
    print('OK')
if __name__ == '__main__':
    main()
