import sys
import os
import time
import threading
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redis_config import r
from worker import extraction_worker

class SimpleQueue:
    def __init__(self, redis_conn):
        self.redis = redis_conn
        self.queue_key = "web_extraction_queue"
        self.processing_key = "web_extraction_queue:processing"
    
    def enqueue(self, func, *args, **kwargs):
        """Add a job to the queue"""
        job = {
            'func': func.__name__,
            'args': args,
            'kwargs': kwargs
        }
        self.redis.lpush(self.queue_key, json.dumps(job))
        return True
    
    def dequeue(self):
        """Get a job from the queue"""
        result = self.redis.brpop(self.queue_key, timeout=1)
        if result:
            return json.loads(result[1])
        return None
    
    def process_job(self, job_data):
        """Execute a job"""
        if job_data['func'] == 'extraction_worker':
            return extraction_worker(*job_data['args'])
        else:
            print(f"Unknown function: {job_data['func']}")

def run_worker():
    """Simple worker that processes jobs"""
    queue = SimpleQueue(r)
    print("Starting simple worker (Windows compatible)...")
    print("Listening for jobs...")
    
    while True:
        try:
            job = queue.dequeue()
            if job:
                print(f"Processing job: {job}")
                result = queue.process_job(job)
                print(f"Job completed: {result}")
            else:
                time.sleep(0.1)  # Small delay to prevent busy waiting
        except KeyboardInterrupt:
            print("Worker stopped by user")
            break
        except Exception as e:
            print(f"Error processing job: {e}")

if __name__ == '__main__':
    run_worker()
