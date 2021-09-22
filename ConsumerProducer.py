import time
from collections import deque
from typing import Callable

from AsyncScheduler import Scheduler, DelayedFunction

class AsyncQueue:
  def __init__(self, sched: Scheduler):
    self.queue = deque()
    self.waiting_gets = deque()
    self.sched = sched
  
  def put(self, val):
    self.queue.append(val)
    if self.waiting_gets:
      func = self.waiting_gets.popleft()
      self.sched.call_soon(func)
  
  def get(self, callback: Callable):
    # wait till an item is available
    if self.queue:
      callback(self.queue.popleft())
    else:
      self.waiting_gets.append(lambda: self.get(callback))

sched = Scheduler()

def async_producer(q: AsyncQueue, count: int):
  def _run(i):
    if i < count:
      print(f"Producing {i}")
      q.put(i)
      sched.call_later(1, lambda: _run(i+1))
    else:
      print("Producer done.")
      q.put(None)
  _run(0)

# q -> thread-safe queue
def traditional_producer(q, count):
  for i in range(count):
    print(f"Producing {i}")
    q.put(i)
    time.sleep(1)
  
  print(f"Producer done.")
  q.put(None)         # signaling

def async_consumer(q: AsyncQueue):
  def _consume(item):
    if item is None:
      print("Consumer done.")
    else:
      print(f"Consuming {item}")
      sched.call_soon(lambda: async_consumer(q))
  q.get(callback=_consume)     # with callback

def traditional_consumer(q):
  while True:
    item = q.get()    # waits
    if item is None:
      break
    print(f"Consuming {item}")
  print("Consumer done.")
    
if __name__ == '__main__':
  que = AsyncQueue(sched)
  sched.call_soon(lambda: async_producer(que, 10))
  sched.call_soon(lambda: async_consumer(que))
  sched.run()
