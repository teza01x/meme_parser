import os


telegram_token = ""

data_base = os.path.join(os.path.dirname(__file__), 'database.db')

START_MENU_STATUS = 0
ADD_MEME_STATUS = 1


target_hour_fetch_memes = 6
max_length_of_memes = 50


judges_group = -1111111
channel_to_post = -111111

image_dir_path = "memes/"
fetch_count = 50
subreddit_names = ['memes',
                   'dankmemes',
                   'MemeEconomy',
                   'ComedyCemetery',
                   'PrequelMemes',
                   'terriblefacebookmemes',
                   'funny',
                   'teenagers',
                   '4chan',
                   'comedyhomicide',
                ]
