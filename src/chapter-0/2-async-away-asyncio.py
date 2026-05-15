# import asyncio
# import time
# async def fetch_data():
#     print("fetching data")
#     await asyncio.sleep(1)
#     print("data fetched")
#     return "data"

# async def main():
#     start_time = time.time()
#     print("main function started")
#     result = await fetch_data()
#     print(result)
#     print("main function ended")
#     end_time = time.time()
#     print(f"Time taken: {end_time - start_time} seconds")

# asyncio.run(main())



import asyncio
import time

async def step1():
    print("step1 started")
    await asyncio.sleep(2)
    print("step1 ended")
    return "A"

async def step2(prev='X'):
    print("step2 started")
    await asyncio.sleep(2)
    print("step2 ended")
    return prev + "B"

async def main():
    start_time = time.time()
    print("main function started")
    a = await step1()
    
    b = await step2()
    

    print(b)

    print("main function ended")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

asyncio.run(main())