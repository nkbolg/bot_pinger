import asyncio
import logging
import os
from asyncio import Event

from telethon import TelegramClient, events
from telethon.tl.types import PeerUser

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
number = lambda: os.environ['TELEPHONE_NUMBER']
BOT_LIST = os.environ['BOT_LIST'].split(';')
ADMIN_LIST = map(int, os.environ['ADMINS_LIST'])

asyncio.set_event_loop(asyncio.SelectorEventLoop())

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)





async def process_bots(bot_list, admin_list, client):
    for bot in bot_list:
        logging.info("Sending message to %s", bot)
        msg = await client.send_message(bot, '/start')
        logging.info(msg)
        got_reply = Event()

        @client.on(events.NewMessage(chats=bot))
        async def handler(_):
            got_reply.set()

        await asyncio.sleep(10)
        if not got_reply.is_set():
            for admin_id in admin_list:
                user_entity = await client.get_entity(PeerUser(admin_id))
                await client.send_message(user_entity, f"{bot=} doesn't respond")


async def main():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        while True:
            await process_bots(BOT_LIST, ADMIN_LIST, client)
            await asyncio.sleep(15)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
