import asyncio

async def my_function(delay):
    print('Start {delay}')
    await asyncio.sleep(delay)
    print('Stop {delay}')

asyncio.ensure_future(my_function(3))
print('Scheduled 3')
asyncio.ensure_future(my_function(2))
print('Scheduled 2')
asyncio.ensure_future(my_function(1))
print('Scheduled 1')

loop = asyncio.get_event_loop()

loop.run_forever()