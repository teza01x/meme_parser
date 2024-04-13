import os
import asyncio
import requests
from praw import Reddit
import uuid
import hashlib
from config import *
from async_sql_scripts import *


def file_already_downloaded(url):
    hash_object = hashlib.md5(url.encode())
    filename = hash_object.hexdigest() + os.path.splitext(url)[1]
    return os.path.exists(os.path.join('memes', filename))


async def fetch_memes(subreddit_names, filter_criteria, time_filter, fetch_count):
    fake_user_agent = f"myRedditApp/{uuid.uuid4()}"
    reddit_client = Reddit(client_id='Nrm3QK_rriIOgwxegAxx5w',
                           client_secret='y9Y0RdqnQjKtfsYKTgHkcjw633nDnA',
                           user_agent=fake_user_agent)
    summary = 0
    for subreddit_name in subreddit_names:
        subreddit = reddit_client.subreddit(subreddit_name)
        memes = getattr(subreddit, filter_criteria)(time_filter=time_filter, limit=fetch_count)
        if summary >= fetch_count:
            break
        downloaded = 0
        for submission in memes:
            if downloaded >= fetch_count:
                break
            if not submission.url.endswith(('.jpg', '.jpeg', '.png')) or file_already_downloaded(submission.url):
                continue
            try:
                hash_object = hashlib.md5(submission.url.encode())
                unique_filename = hash_object.hexdigest() + os.path.splitext(submission.url)[1]
                filepath = os.path.join('memes', unique_filename)
                response = requests.get(submission.url)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                downloaded += 1
                summary += 1
                await asyncio.sleep(0.3)
                await add_meme_to_db(unique_filename, 0)
            except Exception as e:
                print(e)
