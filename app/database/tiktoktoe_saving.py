"""
Authors: Michael Marcus & Tammuz Dubnov

TikTok scrapper in the scope of the TikTokToe project. First project of the Fellows program of ITC
The following algorithm scrapes :
• Posts in the TikTok trending page
• User pages associated to each post

Database class, saving tiktok posts, users, hashtags, songs in an SQLite database

Created in June 2020
"""

# Imports
import sqlite3
import pymysql
import os
import contextlib
from env.conf import DB_NAME, SQL_FILE, DB

class TiktokDatabase:
    def __init__(self, flush_db):
        self.db_name = DB_NAME
        self.sql_file = SQL_FILE
        self.connection = None
        self.cursor = None
        self.connect_to_db(flush_db)

    def connect_to_db(self, flush_db):
        """
        Instantiates the connection with the database
        :param flush_db: flag to flush the database
        """
        if flush_db:
            if os.path.exists(self.db_name):
                os.remove(self.db_name)
            sql_file = open(self.sql_file)
            sql_as_string = sql_file.read()
        """
        with contextlib.closing(sqlite3.connect(self.db_name)) as con:  # auto-closes
            with con:  # auto-commits
                cur = con.cursor()
                if flush_db:
                    # Creating the tables
                    cur.executescript(sql_as_string)
        """
        self.connection = pymysql.connect(host=DB['host'],
                                          user=DB['user'],
                                          password=DB['password'],
                                          # db=DB['name'],
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        if flush_db:
            sql_file = open(self.sql_file)
            sql_as_string = sql_file.read()
            self.cursor.execute("DROP DATABASE {}".format(DB['name']))
            self.cursor.execute("CREATE DATABASE {}".format(DB['name']))
            self.cursor.execute("use {}".format(DB['name']))
            ret = sql_as_string.split(';')
            ret = ret[:-1]
            for req in ret:
                self.cursor.execute(req + ";")
        self.connection.commit()

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
        self.cursor.execute('SELECT user_id FROM TikTokUsers WHERE user_name = %s', [user_name])
        temp_user_id = self.cursor.fetchall()[0]['user_id']
        self.cursor.execute(
            """
            INSERT INTO TikTokPost (user_id, number_of_likes, number_of_share, number_of_comments, post_text)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [temp_user_id, self.cast_int(nb_likes), self.cast_int(nb_shares), self.cast_int(nb_comments), post_desc])
        self.connection.commit()

        post_id = self.cursor.lastrowid
        hashtags = [post.split(" ")[0] for post in post_desc.split("#")[1:]]
        for hashs in hashtags:
            self.cursor.execute('SELECT count(*) FROM AllHashtags WHERE hashtag = %s', [hashs])
            if self.cursor.fetchall()[0]['count(*)'] == 0:
                self.cursor.execute("INSERT INTO AllHashtags (hashtag) VALUES (%s)", [hashs])
            self.cursor.execute(
                'INSERT INTO PostHashtags (hash_id, post_id) VALUES ((SELECT hash_id FROM AllHashtags WHERE hashtag = %s), %s)',
                [hashs, post_id])
            self.connection.commit()

        self.cursor.execute('SELECT count(*) FROM AllSongs WHERE song_name = %s', [song])
        if self.cursor.fetchall()[0]['count(*)'] == 0:
            self.cursor.execute('INSERT INTO AllSongs (song_name) VALUES (%s)', [song])
            self.connection.commit()
            song_id = self.cursor.lastrowid
        else:
            self.cursor.execute('SELECT song_id FROM AllSongs WHERE song_name = %s', [song])
            song_id = self.cursor.fetchall()[0]['song_id']
        self.cursor.execute(
            "INSERT INTO Songs (post_id, song_id) VALUES (%s, %s)",
            [post_id, song_id])
        self.connection.commit()

    def save_user(self, user_name, nb_followers, nb_likes, nb_followings, user_desc):
        """
        Saving users information inn the database
        :param user_name: user name
        :param nb_followers: number of followers
        :param nb_likes: number of likes
        :param nb_followings: number of following users
        :param user_desc: user bio
        """
        self.cursor.execute(
            """
            INSERT INTO TikTokUsers 
            (user_name, number_of_followers, number_of_following, number_of_likes, bio_text) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            [user_name, self.cast_int(nb_followers), self.cast_int(nb_followings), self.cast_int(nb_likes), user_desc])
        self.connection.commit()
        hashtags = [post.split(" ")[0] for post in user_desc.split("#")[1:]]
        for hashs in hashtags:
            self.cursor.execute('SELECT count(*) FROM AllHashtags WHERE hashtag = "{}"'.format(hashs))
            if self.cursor.fetchall()[-1][0] == 0:
                self.cursor.execute("INSERT INTO AllHashtags (hashtag) VALUES (?)", [hashs])
                self.connection.commit()
            self.cursor.execute(
                """
                INSERT INTO UserBioHashtags (hash_id, user_id)
                VALUES ((SELECT hash_id FROM AllHashtags WHERE hashtag = ?),
                (SELECT user_id FROM TikTokUsers WHERE user_name = ?))
                """,
                [hashs, user_name])
            self.connection.commit()

    def get_hashtags(self):
        """
        Getting all the saved hashtags
        :return: all the hashtags saved in our DB
        """
        self.cursor.execute('SELECT * FROM AllHashtags')
        hashtags = self.cursor.fetchall()
        return hashtags

    def save_tweet(self, hash_id, twitter_user, text, url):
        """
        Saving a tweet associated to an hashtag
        :param hash_id: hashtag_id
        :param twitter_user: twitter username
        :param text: tweet text
        :param url: tweet url
        """
        self.cursor.execute(
            """
            INSERT INTO Tweets 
            (hash_id, twitter_user, text, url) 
            VALUES (%s, %s, %s, %s)
            """,
            [hash_id, twitter_user, text, url])
        self.connection.commit()


    def cast_int(self, to_cast):
        if to_cast[-1] == 'K':
            to_cast = to_cast[:-1]
            if "." in to_cast:
                to_cast = to_cast.replace(".", "")
                to_cast += "00"
            else:
                to_cast += "000"
        if to_cast[-1] == 'M':
            to_cast = to_cast[:-1]
            if "." in to_cast:
                to_cast = to_cast.replace(".", "")
                to_cast += "00000"
            else:
                to_cast += "000000"
        if to_cast[-1] == 'B':
            to_cast = to_cast[:-1]
            if "." in to_cast:
                to_cast = to_cast.replace(".", "")
                to_cast += "00000000"
            else:
                to_cast += "000000000"
        return int(to_cast)



