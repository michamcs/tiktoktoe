import base64
import requests
from env.conf import CLIENT_KEY, CLIENT_SECRET


class twitter_calls:
    def __init__(self):
        key_secret = '{}:{}'.format(CLIENT_KEY, CLIENT_SECRET).encode('ascii')
        b64_encoded_key = base64.b64encode(key_secret)
        b64_encoded_key = b64_encoded_key.decode('ascii')
        self.base_url = 'https://api.twitter.com/'
        auth_url = '{}oauth2/token'.format(self.base_url)
        auth_headers = {
            'Authorization': 'Basic {}'.format(b64_encoded_key),
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

        auth_data = {
            'grant_type': 'client_credentials'
        }

        auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
        self.access_token = auth_resp.json()['access_token']

    def query(self, hashtag):
        assert isinstance(hashtag, str), hashtag + " should be a string"
        search_headers = {
            'Authorization': 'Bearer {}'.format(self.access_token)
        }

        search_params = {
            'q': hashtag,
            'result_type': 'popular',
            'count': 100, #limited to 15 by twitter
            'lang': 'en'
        }

        search_url = '{}1.1/search/tweets.json'.format(self.base_url)
        search_resp = requests.get(search_url, headers=search_headers, params=search_params)
        tweet_data = search_resp.json()
        tweets = []
        for i in range(len(tweet_data['statuses'])):
            tweet_text = tweet_data['statuses'][i]['text'].split("https://")
            tweets.append((tweet_data['statuses'][i]['user']['screen_name'],tweet_text[0],"https://"+tweet_text[1]))
        return tweets
