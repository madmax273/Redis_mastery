import time

def extraction_worker(message):
    """Simple worker function that processes a message"""
    print(f"Worker processing message: {message}")
    # Simulate some work
    time.sleep(2)
    print(f"Worker finished processing: {message}")
    return f"Processed: {message}"
