import time
from collections import deque

"""
Minimal async scheduler
"""
class Scheduler:
    def __init__(self):
        self.ready = deque()
    
    def call_soon(self, func):
        self.ready.append(func)
    
    def run(self):
        while self.ready:
            func = self.ready.popleft()
            func()

sched = Scheduler()

def countdown(n):
    if n > 0:
        print(f"Down {n}")
        time.sleep(1)
        sched.call_soon(lambda: countdown(n-1))

def countup(n, i=1):
    if i <= n:
        print(f"Up {i}")
        time.sleep(1)
        sched.call_soon(lambda: countup(n, i+1))

sched.call_soon(lambda: countdown(5))
sched.call_soon(lambda: countup(5, 1))
sched.run()
