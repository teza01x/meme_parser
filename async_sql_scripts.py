import aiosqlite
import asyncio
import random
from config import *


async def check_user_exists(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user WHERE user_id = ?", (user_id,))
            user = await result.fetchall()
        return bool(len(user))


async def add_user_to_db(user_id, username):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO user (user_id, username, meme_limit, menu_status) VALUES(?, ?, ?, ?)", (user_id, username, 3, 0,))
            await conn.commit()


async def update_username(user_id, username):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET username = ? WHERE user_id = ?", (username, user_id,))
            await conn.commit()


async def change_menu_status(user_id, status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET menu_status = ? WHERE user_id = ?", (status, user_id,))
            await conn.commit()


async def get_user_status(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT menu_status FROM user WHERE user_id = ?", (user_id,))
            user_status = await result.fetchone()
            return user_status[0]


async def get_uniq_ids():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            uniq_id_fetch = await cursor.execute("SELECT uniq_id FROM memes")
            uniq_ids = await uniq_id_fetch.fetchall()
            return [i[0] for i in uniq_ids]


async def add_meme_to_db(meme_name, from_user):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            uniq_ids = await get_uniq_ids()
            while True:
                uniq_id = random.randint(1, 999999999)
                if uniq_id not in uniq_ids:
                    break
            score = 0
            if from_user == 1:
                score = 1
            await cursor.execute("INSERT INTO memes (meme, voted_users, published, send_groups, score, from_user, queue, uniq_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (meme_name, "", 0, "", score, from_user, 0, uniq_id,))
            await conn.commit()


async def spend_meme_limit(user_id, limit_change):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            meme_limit_fetch = await cursor.execute("SELECT meme_limit FROM user WHERE user_id = ?", (user_id,))
            meme_limit = await meme_limit_fetch.fetchone()
            current_limit = meme_limit[0]

            current_limit = current_limit - limit_change

            await cursor.execute("UPDATE user SET meme_limit = ? WHERE user_id = ?", (current_limit, user_id,))
            await conn.commit()


async def get_meme_limit(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            meme_limit_fetch = await cursor.execute("SELECT meme_limit FROM user WHERE user_id = ?", (user_id,))
            meme_limit = await meme_limit_fetch.fetchone()
            return meme_limit[0]


async def get_list_of_active_memes():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            memes_fetch = await cursor.execute("SELECT uniq_id FROM memes WHERE published = ? AND from_user = ?", (0, 0,))
            memes_from_reddit = await memes_fetch.fetchall()
            memes_from_reddit = [i[0] for i in memes_from_reddit]


            memes_from_user_fetch = await cursor.execute("SELECT uniq_id FROM memes WHERE published = ? AND from_user = ?", (0, 1,))
            memes_from_user = await memes_from_user_fetch.fetchall()
            memes_from_user = [i[0] for i in memes_from_user]

            return memes_from_reddit, memes_from_user


async def get_list_of_active_memes_v2():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            memes_fetch = await cursor.execute("SELECT uniq_id FROM memes WHERE published = ?", (1,))
            memes = await memes_fetch.fetchall()
            return [i[0] for i in memes]


async def get_meme_score(meme):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            meme_score_fetch = await cursor.execute("SELECT score FROM memes WHERE uniq_id = ?", (meme,))
            meme_score = await meme_score_fetch.fetchone()
            return meme_score[0]


async def get_voted_users(meme):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            voted_users_fetch = await cursor.execute("SELECT voted_users FROM memes WHERE uniq_id = ?", (meme,))
            voted_users = await voted_users_fetch.fetchone()
            result_list = [i for i in voted_users[0].split(":") if len(i) > 0]
            return result_list


async def update_meme_score_positive(meme, user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            users_voted = await get_voted_users(meme)
            if str(user_id) not in users_voted:
                meme_score_fetch = await cursor.execute("SELECT score FROM memes WHERE uniq_id = ?", (meme,))
                meme_score = await meme_score_fetch.fetchone()
                score = meme_score[0]
                updated_score = score + 1

                add_user = str(user_id) + ":"
                users_voted.append(add_user)
                users_voted_list_to_update = ":".join(users_voted)

                await cursor.execute("UPDATE memes SET score = ?, voted_users = ? WHERE uniq_id = ?", (updated_score, users_voted_list_to_update, meme,))
                await conn.commit()
                return True
            else:
                return False


async def update_meme_score_negative(meme, user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            users_voted = await get_voted_users(meme)
            if str(user_id) not in users_voted:
                meme_score_fetch = await cursor.execute("SELECT score FROM memes WHERE uniq_id = ?", (meme,))
                meme_score = await meme_score_fetch.fetchone()
                score = meme_score[0]
                updated_score = score - 1

                add_user = str(user_id) + ":"
                users_voted.append(add_user)
                users_voted_list_to_update = ":".join(users_voted)

                await cursor.execute("UPDATE memes SET score = ?, voted_users = ? WHERE uniq_id = ?", (updated_score, users_voted_list_to_update, meme,))
                await conn.commit()
                return True
            else:
                return False


async def update_meme_score_neutral(meme, user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            users_voted = await get_voted_users(meme)
            if str(user_id) not in users_voted:
                meme_score_fetch = await cursor.execute("SELECT score FROM memes WHERE uniq_id = ?", (meme,))
                meme_score = await meme_score_fetch.fetchone()
                score = meme_score[0]
                updated_score = score

                add_user = str(user_id) + ":"
                users_voted.append(add_user)
                users_voted_list_to_update = ":".join(users_voted)

                await cursor.execute("UPDATE memes SET score = ?, voted_users = ? WHERE uniq_id = ?", (updated_score, users_voted_list_to_update, meme,))
                await conn.commit()
                return True
            else:
                return False


async def get_meme_published_status(meme):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT published FROM memes WHERE uniq_id = ?", (meme,))
            pub_status = await result.fetchone()
            return pub_status[0]


async def update_meme_published_status(meme, published_status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE memes SET published = ? WHERE uniq_id = ?", (published_status, meme,))
            await conn.commit()


async def update_meme_published_status_v2(meme, published_status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE memes SET published = ? WHERE meme = ?", (published_status, meme,))
            await conn.commit()


async def get_meme_image(meme):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT meme FROM memes WHERE uniq_id = ?", (meme,))
            meme_image = await result.fetchone()
            return meme_image[0]


async def get_fetch_memes_time():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT time FROM task_time WHERE operation = ?", ("fetch_memes",))
            time_operation = await result.fetchone()
            return time_operation[0]


async def update_fetch_time(timestamp):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE task_time SET time = ? WHERE operation = ?", (timestamp, "fetch_memes",))
            await conn.commit()


async def get_send_memes_judges_time():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT time FROM task_time WHERE operation = ?", ("send_meme_judges",))
            time_operation = await result.fetchone()
            return time_operation[0]


async def update_send_memes_judges_time(timestamp):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE task_time SET time = ? WHERE operation = ?", (timestamp, "send_meme_judges",))
            await conn.commit()


async def get_send_memes_to_channel_time():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT time FROM task_time WHERE operation = ?", ("send_meme_channel",))
            time_operation = await result.fetchone()
            return time_operation[0]


async def update_send_memes_to_channel_time(timestamp):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE task_time SET time = ? WHERE operation = ?", (timestamp, "send_meme_channel",))
            await conn.commit()


async def get_send_meme_channel_time():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT time FROM task_time WHERE operation = ?", ("send_meme_channel",))
            time_operation = await result.fetchone()
            return time_operation[0]


async def get_send_meme_judges_time():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT time FROM task_time WHERE operation = ?", ("send_meme_judges",))
            time_operation = await result.fetchone()
            return time_operation[0]


async def get_reset_data_time():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT time FROM task_time WHERE operation = ?", ("reset_data_time",))
            time_operation = await result.fetchone()
            return time_operation[0]


async def update_meme_time_status(meme, published_status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE memes SET published = ? WHERE uniq_id = ?", (published_status, meme,))
            await conn.commit()


async def get_meme_by_score_rate():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT meme, score FROM memes WHERE published = ?", (1,))
            top_memes = await result.fetchall()
            sorted_list = sorted(top_memes, key=lambda x: x[1], reverse=True)
            return sorted_list
