import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redis_config import r
from worker import extraction_worker
from simple_queue import SimpleQueue

# Use simple Windows-compatible queue
queue = SimpleQueue(r)

# suppose this is the list of extraction from website
id_list=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]


def add_message(message):
    print(f"Adding message: {message}")
    # Enqueue with simple queue
    success = queue.enqueue(extraction_worker, message, name="testing website extraction")
    if success:
        print("Message added to queue successfully")
    else:
        print("Failed to add message to queue")
    return success



if __name__ == "__main__":
    for i in id_list:
        add_message(f"extracting website {i}")


