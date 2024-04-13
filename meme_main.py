import asyncio
import aiohttp
import aiofiles
import time
from datetime import datetime, timedelta
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup
from telebot import types
from async_sql_scripts import *
from text_scripts import *
from async_markdownv2 import *
from fetch_memes import *
from config import *


bot = AsyncTeleBot(telegram_token)


@bot.message_handler(commands=['start', 'menu'])
async def start(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        if not await check_user_exists(user_id):
            try:
                await add_user_to_db(user_id, username)
            except Exception as error:
                print(f"Error adding user to db error:\n{error}")
        else:
            await update_username(user_id, username)

        text = await escape(dictionary['start_msg'], flag=0)
        button_list1 = [
            types.InlineKeyboardButton("Send Meme 🌈", callback_data="send_meme"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list1])

        await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

        await change_menu_status(user_id, START_MENU_STATUS)
    except Exception as e:
        print(f"Error in start message: {e}")


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    user_id = call.from_user.id

    if call.data == "send_meme":
        await bot.answer_callback_query(call.id)
        meme_limit = await get_meme_limit(user_id)

        if meme_limit > 0:
            text = await escape(dictionary['send_meme'], flag=0)
            button_list1 = [
                types.InlineKeyboardButton("Back ⬅️", callback_data="start_menu"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

            await change_menu_status(user_id, ADD_MEME_STATUS)
        else:
            text = await escape(dictionary['meme_limit'], flag=0)

            button_list1 = [
                types.InlineKeyboardButton("Back ⬅️", callback_data="start_menu"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
            await change_menu_status(user_id, START_MENU_STATUS)

    elif call.data.startswith("p_score_"):
        meme = call.data.split("_")[2]
        old_score = await get_meme_score(meme)

        vote_result = await update_meme_score_positive(meme, user_id)

        if vote_result == True:
            await bot.answer_callback_query(call.id, text="Your vote has been counted. 👍", show_alert=False)
        else:
            await bot.answer_callback_query(call.id, text="You have already voted for this meme 🗿", show_alert=False)

        score = await get_meme_score(meme)

        if score != old_score:
            button_list1 = [
                types.InlineKeyboardButton(f"Score: {score}", callback_data="score"),
            ]
            button_list2 = [
                types.InlineKeyboardButton("👍", callback_data=f"p_score_{meme}"),
                types.InlineKeyboardButton("🫥", callback_data=f"no_score_{meme}"),
                types.InlineKeyboardButton("👎", callback_data=f"n_score_{meme}"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])
            try:
                await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=reply_markup)
            except:
                pass
    elif call.data.startswith("n_score_"):
        meme = call.data.split("_")[2]
        old_score = await get_meme_score(meme)

        vote_result = await update_meme_score_negative(meme, user_id)

        if vote_result == True:
            await bot.answer_callback_query(call.id, text="Your vote has been counted. 👍", show_alert=False)
        else:
            await bot.answer_callback_query(call.id, text="You have already voted for this meme 🗿", show_alert=False)

        score = await get_meme_score(meme)

        if score != old_score:
            button_list1 = [
                types.InlineKeyboardButton(f"Score: {score}", callback_data="score"),
            ]
            button_list2 = [
                types.InlineKeyboardButton("👍", callback_data=f"p_score_{meme}"),
                types.InlineKeyboardButton("🫥", callback_data=f"no_score_{meme}"),
                types.InlineKeyboardButton("👎", callback_data=f"n_score_{meme}"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])
            try:
                await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=reply_markup)
            except:
                pass

    elif call.data.startswith("no_score_"):
        meme = call.data.split("_")[2]
        old_score = await get_meme_score(meme)

        vote_result = await update_meme_score_negative(meme, user_id)

        if vote_result == True:
            await bot.answer_callback_query(call.id, text="Your vote has been counted. 👍", show_alert=False)
        else:
            await bot.answer_callback_query(call.id, text="You have already voted for this meme 🗿", show_alert=False)

        score = await get_meme_score(meme)

        if score != old_score:
            button_list1 = [
                types.InlineKeyboardButton(f"Score: {score}", callback_data="score"),
            ]
            button_list2 = [
                types.InlineKeyboardButton("👍", callback_data=f"p_score_{meme}"),
                types.InlineKeyboardButton("🫥", callback_data=f"no_score_{meme}"),
                types.InlineKeyboardButton("👎", callback_data=f"n_score_{meme}"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])
            try:
                await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=reply_markup)
            except:
                pass
    elif call.data == "score":
        await bot.answer_callback_query(call.id, text="It's a score counter and nothing more. 🙌", show_alert=False)

    elif call.data == "start_menu":
        await bot.answer_callback_query(call.id)

        text = await escape(dictionary['start_msg'], flag=0)
        button_list1 = [
            types.InlineKeyboardButton("Send Meme 🌈", callback_data="send_meme"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list1])

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

        await change_menu_status(user_id, START_MENU_STATUS)


@bot.message_handler(func=lambda message: True, content_types=["photo"])
async def handle_photo(message):
    chat_type = message.chat.type
    if chat_type == 'private':
        user_id = message.chat.id
        user_status = await get_user_status(user_id)
        meme_limit = await get_meme_limit(user_id)

        if user_status == ADD_MEME_STATUS:
            if meme_limit > 0:
                file_id = message.photo[-1].file_id
                file_info = await bot.get_file(file_id)

                file_url = f'https://api.telegram.org/file/bot{telegram_token}/{file_info.file_path}'
                meme_name = f"{file_id}.jpg"
                file_path = image_dir_path + meme_name

                async with aiohttp.ClientSession() as session:
                    async with session.get(file_url) as response:
                        if response.status == 200:
                            async with aiofiles.open(file_path, 'wb') as f:
                                await f.write(await response.read())

                await add_meme_to_db(meme_name, 1)
                await spend_meme_limit(user_id, 1)

                text = await escape(dictionary['accept_meme'], flag=0)

                button_list1 = [
                    types.InlineKeyboardButton("Back ⬅️", callback_data="start_menu"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])

                await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
                await change_menu_status(user_id, START_MENU_STATUS)
            else:
                text = await escape(dictionary['meme_limit'], flag=0)

                button_list1 = [
                    types.InlineKeyboardButton("Back ⬅️", callback_data="start_menu"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])

                await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup,
                                       parse_mode="MarkdownV2")
                await change_menu_status(user_id, START_MENU_STATUS)


async def mix_memes(reddit_memes, user_memes):
    mixed_memes = []
    reddit_index, user_index = 0, 0

    while len(mixed_memes) < max_length_of_memes and (reddit_index < len(reddit_memes) or user_index < len(user_memes)):
        if reddit_index < len(reddit_memes):
            mixed_memes.extend(reddit_memes[reddit_index:reddit_index+2])
            reddit_index += 2
        if user_index < len(user_memes):
            mixed_memes.append(user_memes[user_index])
            user_index += 1
        mixed_memes = mixed_memes[:max_length_of_memes]

    return mixed_memes


async def meme_send_to_judges():
    while True:
        check_time = await get_send_memes_judges_time()
        current_time = time.time()

        if current_time >= check_time:
            memes_from_reddit, memes_from_user = await get_list_of_active_memes()

            list_of_memes = await mix_memes(memes_from_reddit, memes_from_user)

            for meme in list_of_memes:
                try:
                    score = await get_meme_score(meme)
                    meme_image = await get_meme_image(meme)
                    with open(f'{image_dir_path}{meme_image}', 'rb') as meme_image:

                        button_list1 = [
                            types.InlineKeyboardButton(f"Score: {score}", callback_data="score"),
                        ]
                        button_list2 = [
                            types.InlineKeyboardButton("👍", callback_data=f"p_score_{meme}"),
                            types.InlineKeyboardButton("🫥", callback_data=f"no_score_{meme}"),
                            types.InlineKeyboardButton("👎", callback_data=f"n_score_{meme}"),
                        ]
                        reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])

                        await bot.send_photo(chat_id=judges_group, photo=meme_image, reply_markup=reply_markup)
                except Exception as error:
                    print(error)
                await update_meme_published_status(meme, 1)

            target_hour_fetch_memes = 7

            now = datetime.now()

            next_day = now + timedelta(days=1)
            next_day_at_target_hour = next_day.replace(hour=target_hour_fetch_memes, minute=0, second=0, microsecond=0)

            timestamp = int(datetime.timestamp(next_day_at_target_hour))
            await update_send_memes_judges_time(timestamp)

        await asyncio.sleep(15)


async def fetching_meme_func():
    while True:
        check_time = await get_fetch_memes_time()
        current_time = time.time()

        if current_time >= check_time:
            await fetch_memes(subreddit_names, filter_criteria="top", time_filter="day", fetch_count=fetch_count)

            target_hour_fetch_memes = 6

            now = datetime.now()

            next_day = now + timedelta(days=1)
            next_day_at_target_hour = next_day.replace(hour=target_hour_fetch_memes, minute=0, second=0, microsecond=0)

            timestamp = int(datetime.timestamp(next_day_at_target_hour))
            await update_fetch_time(timestamp)

        await asyncio.sleep(16)


async def generate_next_full_hour_timestamp():
    current_time = datetime.now()

    next_full_hour = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return int(datetime.timestamp(next_full_hour))


async def send_memes_to_channel():
    while True:
        check_time = await get_send_memes_to_channel_time()
        current_time = int(time.time())


        if current_time >= check_time:
            list_of_scored_memes = await get_meme_by_score_rate()

            meme_to_post = list_of_scored_memes[0]

            with open(f'{image_dir_path}{meme_to_post}', 'rb') as meme_image:
                await bot.send_photo(chat_id=channel_to_post, photo=meme_image)

            timestamp = await generate_next_full_hour_timestamp()
            await update_send_memes_to_channel_time(timestamp)
            await update_meme_published_status(meme, 2)

        await asyncio.sleep(17)


async def main():
    try:
        bot_task = asyncio.create_task(bot.polling(non_stop=True, request_timeout=500))
        send_meme_to_judges = asyncio.create_task(meme_send_to_judges())
        send_meme_to_chnl = asyncio.create_task(send_memes_to_channel())
        fetch_daily_meme = asyncio.create_task(fetching_meme_func())
        await asyncio.gather(bot_task, send_meme_to_judges, send_meme_to_chnl, fetch_daily_meme)
    except Exception as error:
        print(error)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
