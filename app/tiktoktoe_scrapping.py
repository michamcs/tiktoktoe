"""
Authors: Michael Marcus & Tammuz Dubnov

TikTok scrapper in the scope of the TikTokToe project. First project of the Fellows program of ITC
The following algorithm scrapes :
• Posts in the TikTok trending page
• User pages associated to each post

Created in June 2020
"""
# Imports
import time
import argparse
import sqlite3
import os
import contextlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from env.conf import URL_TO_SCROLL, DB_NAME
from database.tiktoktoe_saving import TiktokDatabase

class TiktokUser:
    def __init__(self, user_id, user_desc, nb_followings, nb_followers, nb_likes):
        """
        TiktokUser constructor
        :param user_id: user_id
        :param user_desc: short bio about the user
        :param nb_followings: number of members the user follows
        :param nb_followers: user's number of followers
        :param nb_likes: user's number of likes
        """
        self.user_id = user_id
        self.description = user_desc
        self.following = nb_followings
        self.followers = nb_followers
        self.likes = nb_likes

    def __repr__(self):
        """
        TiktokUser representation
        :return: user_id
        """
        return self.user_id

    def __eq__(self, user_id_to_check):
        """
        Defining equality
        :param user_id_to_check: user_id we wnt to check
        :return: Boolean
        """
        return self.user_id == user_id_to_check

class TiktokPost:
    def __init__(self, user_id, post_desc, song, nb_likes, nb_comments, nb_shares):
        """
        Tiktok Post constructor
        :param user_id: post's creator user_id
        :param post_desc: post description
        :param song: post song
        :param nb_likes: number of likes for the post
        :param nb_comments: number of comments for the post
        :param nb_shares: number of shares for the post
        """
        self.user_id_index = user_id  # this is a the TiktokUser index
        self.description = post_desc
        self.song = song
        self.likes = nb_likes
        self.comments = nb_comments
        self.shares = nb_shares


class TiktokScrape:
    def __init__(self, flush_db=True, headless=False, url=URL_TO_SCROLL):
        """
        Scraper constructor
        :param url: url to scrape
        we define more options in the constructor such as users and posts arrays and scraper settings
        """
        self.users = []
        self.posts = []
        self.db = TiktokDatabase(flush_db)
        self.chrome_options = webdriver.ChromeOptions()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("window-size=1920,1080")
        self.chrome_options.add_argument("user-agent='Applebot'")
        self.driver = webdriver.Chrome(r"./chromedriver", options=self.chrome_options)
        self.driver.get(url)

    def check_new_user(self, user_id_to_check):
        """
        Checking if a user was already scrapped. If it is, we do not scrape is personal page again
        :param user_id_to_check: user id we want to check
        :return: Boolean
        """
        if user_id_to_check in self.users:
            return True, self.users.index(user_id_to_check)  # overcoming bug for first user at index 0
        return False, -1

    def scroll(self, num_scrolls=3, print_logs=True):
        """
        Scrolling over the page
        :param print_logs: print_logs flag
        :param num_scrolls: number of scrolls
        :return: Nothing
        """
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_pause_time = 1
        while num_scrolls > 0:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(scroll_pause_time)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            #if new_height == last_height:
               #break  # infinite scroll, so this should never happen
            last_height = new_height
            num_scrolls -= 1
            if print_logs:
                print(f"Scrolling for another {num_scrolls} times")

    def get_posts(self, print_logs=True, scroll_profile=True):
        """
        Scraîng post elements
        :param print_logs: print_logs flag
        :param scroll_profile: Number of scrolls
        :return: Nothing
        """
        main_window = self.driver.current_window_handle
        items = self.driver.find_elements(By.CLASS_NAME, 'video-feed-item')
        i = 0
        for post in items:
            if print_logs:
                print(f'looking at post {i}')
            i += 1
            # Picking post elements
            user_name = post.find_element_by_class_name('author-uniqueId').text
            try:
                title = post.find_element(By.CLASS_NAME, 'item-meta-title')
            except NoSuchElementException:
                post_desc = ''
            else:
                title = title.find_elements_by_xpath('.//strong')
                post_desc = ' '.join([el.text for el in title])
            song = post.find_element(By.CLASS_NAME, 'music-title-decoration').text
            nb_likes = post.find_element_by_css_selector("[title^='like']").text
            nb_comments = post.find_element_by_css_selector("[title^='comment']").text
            nb_shares = post.find_element_by_css_selector("[title^='share']").text

            user, user_index = self.check_new_user(user_name)

            if not user and scroll_profile:
                user_index = self.get_users(user_name, main_window)
            elif user and scroll_profile and print_logs:
                print("This user has already been seen before....")
            # Appending post info to posts array
            self.posts.append(TiktokPost(user_index, post_desc, song, nb_likes, nb_comments, nb_shares))
            self.db.save_post(user_name, nb_likes, nb_shares, nb_comments, post_desc, song)


    def get_users(self, user_name, main_window):
        """
        Switching to the user page
        :param user_name: user_name we want to switch to
        :param main_window: trending tiktok page windows for the fallback
        :return: the new length of the users array
        """
        self.driver.execute_script("window.open('http://www.tiktok.com/@{}', 'new_window')".format(user_name))
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])
        try:
            WebDriverWait(self.driver, 20).until(ec.presence_of_element_located((By.CLASS_NAME, "share-desc")))
        except TimeoutException:
            self.driver.close()
            self.driver.switch_to.window(main_window)
            return -1  # meaning this

        # getting the user info
        try:
            user_desc = self.driver.find_element(By.CLASS_NAME, 'share-desc').text
        except NoSuchElementException:
            user_desc = ''

        try:
            nb_followings = self.driver.find_element_by_css_selector("[title^='Followings']").text

        except NoSuchElementException:
            nb_followings = self.driver.find_element_by_css_selector("[title^='Following']").text

        nb_followers = self.driver.find_element_by_css_selector("[title^='Followers']").text

        nb_likes = self.driver.find_element_by_css_selector("[title^='Likes']").text

        # Appending user info to user df
        self.users.append(TiktokUser(user_name, user_desc, nb_followings, nb_followers, nb_likes))
        self.db.save_user(user_name, nb_followers, nb_likes, nb_followings, user_desc)

        # closing the user page
        self.driver.close()
        self.driver.switch_to.window(main_window)
        return len(self.users) - 1


def define_parser():
    """settings for the parser"""
    parser = argparse.ArgumentParser(description='TikTok Scrapper')
    parser.add_argument("-f", "--flush_db", action="store_true", help="Reinitialize the DB before scrapping",
                        default=True)
    parser.add_argument("-l", "--print_logs", action="store_true", help="Print logs while scrapping")
    parser.add_argument("-he", "--headless", action="store_true", help="Scrape headless")
    parser.add_argument("-s", "--scroll_nb", action="store", nargs="?", const=3, default=3,
                        help="Number of scrolls", type=int)
    return parser.parse_args()

def main():
    args = define_parser()
    scrapping = TiktokScrape(args.flush_db, args.headless)
    scrapping.scroll(args.scroll_nb, args.print_logs)
    scrapping.get_posts(args.print_logs)
    print(f'Got {len(scrapping.posts)} posts')
    print(f'Got {len(scrapping.users)} users')


if __name__ == "__main__":
    main()
