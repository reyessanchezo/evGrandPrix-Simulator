
from tqdm import tqdm
import time
from tqdm.tk import trange
 
 
for i in tqdm (range (101), 
               desc="Loading...", 
               ascii=False, dynamic_ncols=True):
    time.sleep(0.01)

'''
for i in trange(100):
    time.sleep(0.1)
'''
from tqdm.auto import tqdm
from time import sleep


def generator():
    while True:
        sleep(0.3) # iteration stuff
        yield
        
for _ in tqdm(generator()): pass

print("Complete.")
