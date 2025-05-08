import asyncio
import csv
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import CommandStart, Command
import time as t
from datetime import datetime, time


TOKEN = "7436533994:AAGvvnip8IQEY8lo_u7_pmBRtaNb443A6tY"
TIME_LIMIT = 7*24*60*60 # in seconds
MESSAGE = "You have been removed from the group testChannel" # The message the bot will send on removing a member
INVITE_LINK = "https://t.me/+_qB6mDn6etMwMmQ9"

dp = Dispatcher()
lock = asyncio.Lock()
lock2 = asyncio.Lock()

async def scheduled_task(bot: Bot):
    while True:
        await remove_users(bot)
        await asyncio.sleep(3600)  # Wait 1 hr


async def get_csv_data(filename: str) -> list[list]:
    res = []
    async with lock:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for i in reader:
                res.append(i)
    return res

async def write_csv_data(data: list[list], filename, mode='a'):
    async with lock:
        with open(filename, mode, newline="\n") as file:
            writer = csv.writer(file)
            writer.writerows(data)

async def remove_users(bot: Bot):
    async with lock2:
        users = await get_csv_data("data.csv")
        now = t.time()
        removed = []
        try:
            for user in users:
                if now>(float(user[2])+TIME_LIMIT):
                    await bot.ban_chat_member(user[0], user[1])
                    print("Removed: "+ user[0] +" "+ user[1])
                    await bot.send_message(user[1], MESSAGE)
                    users.remove(user)
                    removed.append([user[1], user[3]])
            await write_csv_data(users, "data.csv", mode='w')
            await write_csv_data(removed, "removed_users.csv")
        except Exception as e:
            print("Error in removing: "+e)

@dp.chat_join_request()
async def approve_handler(chat_join_request: types.ChatJoinRequest, bot: Bot):
    try:
        await bot.approve_chat_join_request(
            chat_id=chat_join_request.chat.id,
            user_id=chat_join_request.from_user.id
        )
        async with lock2:
            await write_csv_data([[chat_join_request.chat.id, chat_join_request.from_user.id, t.time(), chat_join_request.from_user.username]], "data.csv")
        
        print(f"Approved join request from user_id: {chat_join_request.from_user.id} chat_id: {chat_join_request.chat.id.__str__()}")
    except Exception as e:
        print(f"Error abbproving join request: {e}")

@dp.message(CommandStart())
async def start_cmd(msg: types.Message):
    await msg.answer("Join the channel using this link\n"+INVITE_LINK)

async def on_startup(bot: Bot):
    asyncio.create_task(scheduled_task(bot))

async def main():
    bot = Bot(TOKEN)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())