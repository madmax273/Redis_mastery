import requests
import time
import threading
from threading import Thread

def single_request(user_id, request_id):
    """Single request function for threading"""
    start_time = time.time()
    try:
        response = requests.get(f"http://localhost:8000/users/{user_id}")
        end_time = time.time()
        if response.status_code == 200:
            user_data = response.json()
            print(f"Request {request_id}: {user_data['name']} - took {end_time - start_time:.3f}s")
        else:
            print(f"Request {request_id}: Failed with status {response.status_code}")
    except Exception as e:
        print(f"Request {request_id}: Error - {e}")

def test_stampede_protection():
    """Simple test to demonstrate stampede protection"""
    print("Testing stampede protection...")
    print("Make sure your server is running and you have a user with ID=1")
    print()
    
    print("Sending 10 concurrent requests...")
    print("Watch the server logs to see stampede protection in action!")
   
    
    # Create and start 10 threads
    threads = []
    start_time = time.time()
    
    for i in range(10):
        thread = Thread(target=single_request, args=(2, i+1))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print(f"\nAll requests completed in {end_time - start_time:.3f}s")

if __name__ == "__main__":
    test_stampede_protection()
