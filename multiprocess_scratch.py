from multiprocessing import Queue, Process, Pool

q = Queue()
q.put(range(10))
print(q.qsize())
