from AsyncScheduler import Scheduler

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
