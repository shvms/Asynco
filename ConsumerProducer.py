import time
from collections import deque
from typing import Callable

from AsyncScheduler import Scheduler

class QueueClosed(Exception):
  pass

class Result:
  def __init__(self, val=None, exc=None):
    self.__val = val
    self.__exc = exc
  
  def get(self):
    if self.__exc:
      raise self.__exc
    return self.__val

class AsyncQueue:
  def __init__(self, sched: Scheduler):
    self.queue = deque()
    self.waiting_gets = deque()
    self.sched = sched
    self._closed = False
  
  def put(self, val):
    if self._closed:
      raise QueueClosed()
    
    self.queue.append(val)
    if self.waiting_gets:
      func = self.waiting_gets.popleft()
      self.sched.call_soon(func)
  
  def get(self, callback: Callable):
    # wait till an item is available
    if self.queue:
      callback(Result(val=self.queue.popleft()))
    else:
      if self._closed:
        callback(Result(exc=QueueClosed()))
      else:
        self.waiting_gets.append(lambda: self.get(callback))

  def close(self):
    self._closed = True
    if self.waiting_gets and not self.queue:
      for func in self.waiting_gets:
        self.sched.call_soon(func)

scheduler = Scheduler()

def async_producer(q: AsyncQueue, count: int):
  def _run(i):
    if i < count:
      print(f"Producing {i}")
      q.put(i)
      scheduler.call_later(1, lambda: _run(i+1))
    else:
      print("Producer done.")
      q.close()
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
  def _consume(result):
    try:
      item = result.get()
      print(f"Consuming {item}")
      scheduler.call_soon(lambda: async_consumer(q))
    except QueueClosed:
      print("Consumer done.")
  q.get(callback=_consume)     # with callback

def traditional_consumer(q):
  while True:
    item = q.get()    # waits
    if item is None:
      break
    print(f"Consuming {item}")
  print("Consumer done.")
    
if __name__ == '__main__':
  que = AsyncQueue(scheduler)
  scheduler.call_soon(lambda: async_producer(que, 10))
  scheduler.call_soon(lambda: async_consumer(que))
  scheduler.run()
