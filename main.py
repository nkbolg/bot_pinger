import asyncio
import logging
import os
from asyncio import Event

from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
from alchemysession import AlchemySessionContainer

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
BOT_LIST = os.environ['BOT_LIST'].split(';')
ADMIN_LIST = map(int, os.environ['ADMINS_LIST'].split(';'))
DATABASE_URL = os.environ['DATABASE_URL']
MSG_TIMEOUT = os.environ.get('MSG_TIMEOUT', 15)

asyncio.set_event_loop(asyncio.SelectorEventLoop())

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)


async def event_wait(evt, timeout):
    try:
        await asyncio.wait_for(evt.wait(), timeout)
    except asyncio.TimeoutError:
        pass
    logging.info("event got: %s", evt.is_set())
    return evt.is_set()


async def process_bots(bot_list, admin_list, client):
    for bot in bot_list:
        logging.info("Sending message to %s", bot)
        msg = await client.send_message(bot, '/start')
        logging.info(msg)
        got_reply = Event()

        @client.on(events.NewMessage(chats=bot))
        async def handler(event):
            got_reply.set()
            await event.message.mark_read()

        if not await event_wait(got_reply, MSG_TIMEOUT):
            for admin_id in admin_list:
                user_entity = await client.get_entity(PeerUser(admin_id))
                logging.info(f"{bot=} doesn't respond")
                await client.send_message(user_entity, f"{bot=} doesn't respond")


async def main():
    container = AlchemySessionContainer(DATABASE_URL)
    session = container.new_session('session_name')
    async with TelegramClient(session, api_id, api_hash) as client:
        while True:
            await process_bots(BOT_LIST, ADMIN_LIST, client)
            logging.info("Sleeping")
            await asyncio.sleep(15*60)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
