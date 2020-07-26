"""
Authors: Michael Marcus & Tammuz Dubnov

TikTok scrapper in the scope of the TikTokToe project. First project of the Fellows program of ITC
The following algorithm scrapes :
• Posts in the TikTok trending page
• User pages associated to each post

Database class

Created in June 2020
"""
# Imports
import sqlite3
import os
import contextlib
from env.conf import DB_NAME, SQL_FILE

class TiktokDatabase:
    def __init__(self, flush_db):
        self.db_name = DB_NAME
        self.sql_file = SQL_FILE
        self.connection(flush_db)

    def connection(self, flush_db):
        """
        Instantiates the connectionn with the database
        :param flush_db: flag to flush the database
        """
        if flush_db:
            if os.path.exists(self.db_name):
                os.remove(self.db_name)
            sql_file = open(self.sql_file)
            sql_as_string = sql_file.read()

        with contextlib.closing(sqlite3.connect(self.db_name)) as con:  # auto-closes
            with con:  # auto-commits
                cur = con.cursor()
                if flush_db:
                    # Creating the tables
                    cur.executescript(sql_as_string)

    def save_post(self, user_name, nb_likes, nb_shares, nb_comments, post_desc, song):
        """
        Saving post information
        :param user_name: user name
        :param nb_likes: number of post likes
        :param nb_shares: number of shares
        :param nb_comments: number of comments
        :param post_desc: post description
        :param song: post song
        """
        with contextlib.closing(sqlite3.connect(self.db_name)) as con:  # auto-closes
            with con:  # auto-commits
                cur = con.cursor()
                cur.execute('SELECT user_id FROM TikTokUsers WHERE user_name = ?', [user_name])
                temp_user_id = cur.fetchall()[-1][0]
                cur.execute(
                    "INSERT INTO TikTokPost (user_id, number_of_likes, number_of_share, number_of_comments, post_text) VALUES (?, ?, ?, ?, ?)",
                    [temp_user_id, nb_likes, nb_shares, nb_comments, post_desc])

                post_id = cur.lastrowid
                hashtags = [post.split(" ")[0] for post in post_desc.split("#")[1:]]
                for hashs in hashtags:
                    cur.execute('SELECT count(*) FROM AllHashtags WHERE hashtag = "{}"'.format(hashs))
                    if cur.fetchall()[-1][0] == 0:
                        cur.execute("INSERT INTO AllHashtags (hashtag) VALUES (?)", [hashs])
                    cur.execute(
                        'INSERT INTO PostHashtags (hash_id, post_id) VALUES ((SELECT hash_id FROM AllHashtags WHERE hashtag = ?), ?)',
                        [hashs, post_id])

                cur.execute('SELECT COUNT(*) FROM AllSongs WHERE song_name = ?', [song])
                if cur.fetchall()[-1][0] == 0:
                    cur.execute('INSERT INTO AllSongs (song_name) VALUES (?)', [song])
                    song_id = cur.lastrowid
                else:
                    cur.execute('SELECT song_id FROM AllSongs WHERE song_name = "{}"'.format(song))
                    song_id = cur.fetchall()[-1][0]
                cur.execute(
                    "INSERT INTO Songs (post_id, song_id) VALUES (?, ?)",
                    [post_id, song_id])

    def save_user(self, user_name, nb_followers, nb_likes, nb_followings, user_desc):
        """
        Saving users information inn the database
        :param user_name: user name
        :param nb_followers: number of followers
        :param nb_likes: number of likes
        :param nb_followings: number of following users
        :param user_desc: user bio
        """
        with contextlib.closing(sqlite3.connect(self.db_name)) as con:  # auto-closes
            with con:  # auto-commits
                cur = con.cursor()
                cur.execute(
                    """
                    INSERT INTO TikTokUsers 
                    (user_name, number_of_followers, number_of_following, number_of_likes, bio_text) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [user_name, nb_followers, nb_followings, nb_likes, user_desc])
                hashtags = [post.split(" ")[0] for post in user_desc.split("#")[1:]]
                for hashs in hashtags:
                    cur.execute('SELECT count(*) FROM AllHashtags WHERE hashtag = "{}"'.format(hashs))
                    if cur.fetchall()[-1][0] == 0:
                        cur.execute("INSERT INTO AllHashtags (hashtag) VALUES (?)", [hashs])
                    cur.execute(
                        """
                        INSERT INTO UserBioHashtags (hash_id, user_id)
                        VALUES ((SELECT hash_id FROM AllHashtags WHERE hashtag = ?),
                        (SELECT user_id FROM TikTokUsers WHERE user_name = ?))
                        """,
                        [hashs, user_name])
