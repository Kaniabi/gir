import redis
import rq
import worker

q = rq.Queue(connection=redis.Redis())
q.enqueue(worker.SendMessage, 'message')
