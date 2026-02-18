import time
import asyncio
list=[]

# def sleeper1():
#     print("Sleeper 1")
#     time.sleep(1)
#     print("Sleeper 1 done")

# def sleeper2():
#     print("Sleeper 2")
#     time.sleep(2)     
#     print("Sleeper 2 done")

# def sleeper3():
#     print("Sleeper 3")
#     time.sleep(3)     
#     print("Sleeper 3 done")


# def add_message(message):
#      for i in range(0,5):
#        print(f"Adding message {i}") 
#        sleeper1()
#        sleeper2()
#        sleeper3() 
#        print(time.time())

# =========================above example is of synchronous execution======================

async def sleeper1():
    print("Sleeper 1")
    await asyncio.sleep(1)
    print("Sleeper 1 done")

async def sleeper2():
    print("Sleeper 2")
    asyncio.sleep(2)     
    print("Sleeper 2 done")

async def sleeper3():
    print("Sleeper 3")
    asyncio.sleep(3)     
    print("Sleeper 3 done")


async def add_message(message):
     for i in range(0,5):
       print(f"Adding message {i}") 
       await sleeper1()
       await sleeper2()
       await sleeper3()
       print(time.time())

# =========================above example is of asynchronous execution======================
#but both above as same result because each function is called sequentially and this function will make other functions like this in parallel but this function will take as much time as much they are taking because we are awaitng and telling them to stop till these aleeps are done see async doc

# async def sleeper1():
#     print("Sleeper 1")
#     await asyncio.sleep(1)
#     print("Sleeper 1 done")

# async def sleeper2():
#     print("Sleeper 2")
#     await asyncio.sleep(2)     
#     print("Sleeper 2 done")

# async def sleeper3():
#     print("Sleeper 3")
#     await asyncio.sleep(3)     
#     print("Sleeper 3 done")


# async def add_message1(message):
#      for i in range(0,5):
#        print(f"Adding message 1 {i}") 
#        await asyncio.gather(sleeper1(), sleeper2(), sleeper3())
#        print(time.time())

# async def add_message2(message):
#      for i in range(0,5):
#        print(f"Adding message 2 {i}") 
#        await asyncio.gather(sleeper1(), sleeper2(), sleeper3())
#        print(time.time())       

# =========================above example is of asynchronous execution======================
#but both above as same result because each function is called sequentially




async def main():
    await add_message("test")

if __name__ == "__main__":
    asyncio.run(main())
    
    

