import time
from collections import deque
import heapq
from dataclasses import dataclass
from typing import Callable

@dataclass
class DelayedFunction:
  deadline: int
  func: Callable
  
  def __lt__(self, other):
    return self.deadline < other.deadline

"""
Minimal async scheduler
"""
class Scheduler:
  def __init__(self):
    self.ready = deque()
    self.sleeping_funcs = []    # list of tuples of (invoke_time, func)
  
  def call_soon(self, func):
    self.ready.append(func)
  
  def call_later(self, delay, func):
    heapq.heappush(self.sleeping_funcs, DelayedFunction(delay + time.time(), func))
  
  def run(self):
    while self.ready or self.sleeping_funcs:
      if not self.ready:
        closest_delayed_func = heapq.heappop(self.sleeping_funcs)
        delta = closest_delayed_func.deadline - time.time()
        if delta > 0:
          time.sleep(delta)
        self.ready.append(closest_delayed_func.func)
    
      while self.ready:
        func = self.ready.popleft()
        func()

sched = Scheduler()

def countdown(n):
  if n > 0:
    print(f"Down {n}")
    # time.sleep(4)
    sched.call_later(4, lambda: countdown(n-1))

def countup(n, i=1):
  if i <= n:
    print(f"Up {i}")
    # time.sleep(1)
    sched.call_later(1, lambda: countup(n, i+1))

sched.call_soon(lambda: countdown(5))
sched.call_soon(lambda: countup(20, 1))
sched.run()
