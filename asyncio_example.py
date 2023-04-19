import asyncio
import itertools
import pprint
from db import engine, Session, Base, Person
import aiohttp
import datetime

import requests
from more_itertools import chunked

CHUNK_SIZE = 3
async def get_person(people_is, session):
    async with session.get(f'https://swapi.dev/api/people/{people_is}') as response:
        json_data = await response.json()
        json_data['id'] = people_is
        print(f'{people_is} finished')
        return json_data

async def main():
    start = datetime.datetime.now()
    #
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = aiohttp.ClientSession()
    coros = [get_person(session=session, people_is=i) for i in range(1, 100)]
    for c_chunked in chunked(coros, CHUNK_SIZE):
        start_time = datetime.datetime.now()
        charakters = []
        result = await asyncio.gather(*c_chunked)
        for res in result:
            if res.get('created') != None:
                res.pop('created')
            if res.get('edited') != None:
                res.pop('edited')
            res['films'] = await get_str(res['films'])
            res['species'] = await get_str(res['species'])
            res['starships'] = await get_str(res['starships'])
            res['vehicles'] = await get_str(res['vehicles'])
            charakters.append(res)
        asyncio.create_task(paste_to_db(charakters))
        print(datetime.datetime.now() - start_time)
    await session.close()
    tasks = asyncio.all_tasks()
    for task in tasks:
        if task != asyncio.current_task():
            await task
    print(datetime.datetime.now()-start)

async def get_str(some_list: list):
    if len(some_list) != 0:
        session_1 = aiohttp.ClientSession()
        coros = [get_list(link=link, session=session_1) for link in some_list]
        data = ", ".join(await asyncio.gather(*coros))
        await session_1.close()
        return data
    else:
        return ''

async def get_list(link, session):
    async with session.get(link) as response:
        answer = await response.json()
        if answer.get('title') != None:
            return answer['title']
        elif answer.get('name') != None:
            return answer['name']

async def paste_to_db(data):
    persons = [Person(json=jsons) for jsons in data]
    async with Session() as session_db:
        session_db.add_all(persons)
        await session_db.commit()


if __name__ == '__main__':
    asyncio.run(main())