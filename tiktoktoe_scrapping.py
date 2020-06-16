"""
Authors: Michael Marcus & Tammuz Dubnov
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# Scrolling
# TODO: add failed user info attempts as empyt tiktok_user objects / maybe add a list of failed user attempts
# so that we can later a fix that tries to access those user pages after an extended period of time

class tiktok_user():
    def __init__(self, user_id, user_desc, nb_followings, nb_followers, nb_likes):
        self.user_id = user_id
        self.description = user_desc
        self.following = nb_followings
        self.followers = nb_followers
        self.likes = nb_likes
    ## do we have user's actual name?

    def __repr__(self):
        return self.user_id

    def __eq__(self, other_id):
        return self.user_id == other_id

class tiktok_post():
    def __init__(self, user_id, post_desc, song, nb_likes, nb_comments, nb_shares):
        self.user_id_index = user_id  # this is a the tiktok_user index
        self.description = post_desc
        self.song = song
        self.likes = nb_likes
        self.comments = nb_comments
        self.shares = nb_shares
        # do we have post_id?
        # later add each_comment as [] with each comment appended


class tiktok_scrape():
    def __init__(self, url="https://www.tiktok.com/trending"):
        self.users = []
        self.posts = []
        self.chrome_options = webdriver.ChromeOptions()
        # TODO add headless
        self.chrome_options.add_argument("user-agent='Applebot'")
        self.driver = webdriver.Chrome(r"./chromedriver", options=self.chrome_options)
        self.driver.get(url)

    def new_user(self, other_id):
        if other_id in self.users:
            return True, self.users.index(other_id) # overcoming bug for first user at index 0
        return False, -1

    def scroll(self, num_scrolls=3):
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
            if new_height == last_height:
                break  # infinit scroll, so this should never happen
            last_height = new_height
            num_scrolls -= 1
            print(f"Scrolling for another {num_scrolls} times")

    def get_posts(self):
        # Picking elements
        main_window = self.driver.current_window_handle
        items = self.driver.find_elements(By.CLASS_NAME, 'video-feed-item')
        i = 0
        for post in items:
            print(f'looking at post {i}')
            i += 1
            # Picking post elements
            user_id = post.find_element_by_class_name('author-uniqueId').text
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

            user, user_index = self.new_user(user_id)

            if not user:
                user_index = self.get_users(user_id, main_window)
            else:
                print("This user has already been seen before.............................")
            # Appending post info to post df
            self.posts.append(tiktok_post(user_index, post_desc, song, nb_likes, nb_comments, nb_shares))

    def get_users(self, user_id, main_window):
        # switching to the user page
        self.driver.execute_script("window.open('http://www.tiktok.com/@{}', 'new_window')".format(user_id))
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])
        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "share-desc")))
        except TimeoutException:
            self.driver.close()
            self.driver.switch_to.window(main_window)
            return -1 #meaning this

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
        self.users.append(tiktok_user(user_id, user_desc, nb_followings, nb_followers, nb_likes))

        # closing the user page
        self.driver.close()
        self.driver.switch_to.window(main_window)
        return len(self.users)-1

def main():
    scrapping = tiktok_scrape()
    scrapping.scroll(5)
    scrapping.get_posts()
    print(f'Got {len(scrapping.posts)} posts')
    print(f'Got {len(scrapping.users)} users')


if __name__ == "__main__":
    main()
