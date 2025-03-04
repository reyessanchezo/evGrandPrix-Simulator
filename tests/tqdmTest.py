
from tqdm import tqdm
import time
 
 
for i in tqdm (range (101), 
               desc="Loading...", 
               ascii=False, dynamic_ncols=True):
    time.sleep(0.01)
     
print("Complete.")
