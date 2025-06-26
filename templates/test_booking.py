# test_booking.py 
import timeit
from booking import confirm_booking 

# Timeit benchmarking 
setup_code = ''' 
from booking import confirm_booking 
destinations = ['tokyo', ' sydney', '  new york '] * 1000 
'''
exec_time = timeit.timeit("confirm_booking(destinations)", setup=setup_code, number=100) 
print(f"Average time over 100 runs: {exec_time:.4f} seconds") 

import cProfile  

# cProfile with runctx (provides local context to string command) 

destinations = ['tokyo', ' sydney', '  new york '] * 1000 
cProfile.runctx("confirm_booking(destinations)", globals(), locals()) 
