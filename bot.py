import aiohttp

from aiogram import Bot, types  # type: ignore
from aiogram.dispatcher import Dispatcher  # type: ignore
from aiogram.utils import executor  # type: ignore
from helpers import config, process_response

from keybord import WrappedInlineKeyboardMarkup


bot = Bot(token=config["token"])
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    await message.reply("Привет! Какой фильм ты бы хотел сегодня посмотреть?🥰")


@dp.message_handler(commands=['help'])
async def handle_help(message: types.Message):
    await message.reply("Telegram бот, который поможет вам найти фильмы и сериалы, "
                        "даст по ним краткую информацию и подскажет, где можно посмотреть их прямо сейчас.")


@dp.message_handler()
async def echo(message: types.Message):
    async with aiohttp.ClientSession() as session:
        params = {"api_key": config["api_key"], "query": message.text}
        async with session.get(f"{config['api_search_url']}/{'search/movie'}", params=params) as response:
            search_movie_results = (await response.json())["results"]

    films = await process_response(search_movie_results)
    if not films:
        output_message = config["NOT_FOUND_RESPONSE"]
        await bot.send_message(message.chat.id, text=output_message)
    else:
        for film in films:
            output_message = "● {}\n📅: {}\t⭐️ {}\t\n{}".format(
                film["title"], film["year"], film["rating"], film["overview"])

            if not film["link"]:
                await bot.send_photo(message.chat.id, film["poster"],
                                     output_message + "\n\n There are no providers in Russia")
            else:
                keyboard = WrappedInlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton("Providers", film["link"]))
                await bot.send_photo(message.chat.id, film["poster"], output_message,
                                     parse_mode=types.ParseMode.HTML, reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
