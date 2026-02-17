import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import requests

async def test_with_aiohttp():
    """Test using aiohttp for async requests"""
    print("=== Testing with aiohttp (async) ===")
    
    async def fetch_user(session, user_id, request_id):
        start_time = time.time()
        try:
            async with session.get(f"http://localhost:8000/users/{user_id}") as response:
                result = await response.json()
                end_time = time.time()
                print(f"Request {request_id}: {result['name']} (took {end_time - start_time:.3f}s)")
                return result
        except Exception as e:
            print(f"Request {request_id} failed: {e}")
            return None
    
    # Clear cache first
    try:
        requests.delete("http://localhost:8000/users/1")
    except:
        pass
    
    # Send 20 concurrent requests
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(20):
            task = fetch_user(session, 1, i+1)
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"Total time for 20 requests: {end_time - start_time:.3f}s")

def test_with_threads():
    """Test using ThreadPoolExecutor"""
    print("\n=== Testing with ThreadPoolExecutor ===")
    
    def fetch_user(user_id, request_id):
        start_time = time.time()
        try:
            response = requests.get(f"http://localhost:8000/users/{user_id}")
            result = response.json()
            end_time = time.time()
            print(f"Request {request_id}: {result['name']} (took {end_time - start_time:.3f}s)")
            return result
        except Exception as e:
            print(f"Request {request_id} failed: {e}")
            return None
    
    # Clear cache first
    try:
        requests.delete("http://localhost:8000/users/1")
    except:
        pass
    
    # Send 20 concurrent requests
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for i in range(20):
            future = executor.submit(fetch_user, 1, i+1)
            futures.append(future)
        
        start_time = time.time()
        results = [future.result() for future in futures]
        end_time = time.time()
        
        print(f"Total time for 20 requests: {end_time - start_time:.3f}s")

def test_with_curl():
    """Generate curl commands for manual testing"""
    print("\n=== Curl commands for manual testing ===")
    print("Run these commands simultaneously in different terminals:")
    print()
    
    for i in range(10):
        print(f"curl -w 'Request {i+1}: %{time_total}s\\n' -o /dev/null -s http://localhost:8000/users/1 &")
    
    print("wait  # Wait for all background jobs to complete")

def test_with_ab():
    """ApacheBench for load testing"""
    print("\n=== ApacheBench command ===")
    print("Install ApacheBench first, then run:")
    print("ab -n 50 -c 10 http://localhost:8000/users/1")
    print("-n 50: total 50 requests")
    print("-c 10: 10 concurrent requests")

if __name__ == "__main__":
    print("Stampede Protection Testing Tool")
    print("Make sure your FastAPI server is running on localhost:8000")
    print("And you have at least one user with ID=1 in your database")
    print()
    
    # Test with different methods
    asyncio.run(test_with_aiohttp())
    test_with_threads()
    test_with_curl()
    test_with_ab()
