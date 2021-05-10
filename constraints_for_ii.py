import csv
import math
def _closest_factors( n ):
    assert( n > 0 ), 'System size must be greater than 0'

    test_num = int( math.sqrt( n ) )
    while (n % test_num ) != 0:
        test_num = test_num - 1

    x = test_num
    y = n / test_num
    assert( x == int( x ) )
    assert( y == int( y ) )
    x = int(x)
    y = int(y)

    return x, y

def _is_prime(n):
    if n == 2 or n == 3: return True
    if n < 2 or n%2 == 0: return False
    if n < 9: return True
    if n%3 == 0: return False
    r = int(n**0.5)
    # since all primes > 3 are of the form 6n ± 1
    # start with f=5 (which is prime)
    # and test f, f+2 for being prime
    # then loop by 6.
    f = 5
    while f <= r:
        if n % f == 0: return False
        if n % (f+2) == 0: return False
        f += 6
    return True

FULL_DEVICE_X = 19
FULL_DEVICE_Y = 69
# print('benchmark,ii,+ers,*ers,IOers,chip_unroll')

print('benchmark,ii,Nx,Ny,+,*,IO,+ers,*ers,IOers,dfg_unroll,chip_unroll')
rowcount = -1
with open('ops_from_vivado_comparison.csv', newline='') as csvfile:
    opreader = csv.reader(csvfile, delimiter=',')
    for row in opreader:
        rowcount += 1
        if rowcount == 0: continue

        for ii in range(2,6):
            benchmark, adds, multiplies, ios = row[0],int(row[1]),int(row[2]),int(row[3])
            unroll = 1
            if (adds < ii and adds != 0) or (multiplies < ii and multiplies != 0) or (ios < ii and ios != 0):

                unroll = ii

                adds = adds * unroll
                multiplies = multiplies * unroll
                ios = ios * unroll
            
            adders = adds // ii
            multipliers = multiplies // ii
            ioers = ios // ii    

            system_size = adders + multipliers + ioers
            while _is_prime( system_size ):
            
                system_size = system_size + 1


            Nx, Ny = _closest_factors( system_size )
            

            unroll_x = FULL_DEVICE_X // Nx
            unroll_y = FULL_DEVICE_Y // Ny
            chip_unroll = unroll_x * unroll_y * unroll
            # import pdb; pdb.set_trace() 
            print(benchmark+","+str(ii)+","+str(Nx)+","+str(Ny)+","+str(adds)+","+str(multiplies)+","+str(ios)+","+str(adders)+","+str(multipliers)+","+str(ioers)+","+str(unroll)+","+str(chip_unroll))

            # print(benchmark+","+str(ii)+","+str(adders)+","+str(multipliers)+","+str(ioers)+","+str(chip_unroll))