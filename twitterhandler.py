import logging
import urllib
from webapp2_extras import json
from lib.httplib2 import Http
import lib.oauth2 as oauth

import logging

logging.basicConfig(filename='/var/log/app_engine/custom_logs/tweet_handler_log.log',level=logging.DEBUG)

CONSUMER_KEY ="p16si9qxR6bVxBgTM9OQwNTYQ"
CONSUMER_KEY_SECRET = "EKokaSHbD66k1Cg4IYMfnsvdImLP47QrYP7IMBm0qZaQBb9o9k"
CONDITION_TOKEN = "725685966-BaMrcdqWQw8zvA3hKknHXljaLoJWH2nl1ddmqDRe"
CONDITION_TOKEN_SECRET = "i6VE7HKP39Oilcd9pnXHDsDhiouVeUUbOlv9d5IK1komP"

DEFAULT_SEARCH_SIZE = 30

class TwitterHandler:
    "Contains functions that deal with twitter"
    def __init__(self, search_val, since_id = long(-1)):
        self.search_val = search_val
        self.since_id = since_id

    def retrieveData(self, number_of_tweets = DEFAULT_SEARCH_SIZE):
        logging.info("Search key : " + self.search_val)                                                                          #logging

        #Checking if empty string has been provided
        if not self.search_val or self.search_val.isspace():
            return list()

        #Getting auth client
        consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_KEY_SECRET)
        condition_token = oauth.Token(key=CONDITION_TOKEN, secret=CONDITION_TOKEN_SECRET)
        client = oauth.Client(consumer, condition_token)

        final_list = list()

        twit_max_id = long('-1')

        request_count = 0                                                                                                        #LOG DATA
        loop_condition = True
        while(loop_condition):
            request_url = 'https://api.twitter.com/1.1/search/tweets.json?q='
            result_type = '&result_type=recent'
            tweet_count = '&count=100'
            stub_max_id = '&max_id='
            stub_sin_id = '&since_id='

            #we form the GET url
            query = request_url + '"' + urllib.quote_plus(self.search_val) + '"' + result_type + tweet_count
            
            if twit_max_id > 0:
                query += stub_max_id + `twit_max_id`

            if self.since_id > 0:
                query += stub_sin_id + `self.since_id`

            logging.info("Search query : " + query)                                                                              #logging                       

            #actually firing the query
            response, data = client.request(query)

            logging.info("Server Response : " + query)                                                                           #logging

            decoded_data = json.decode(data)

            #returning if error encountered
            if "errors" in decoded_data:
                if (len(final_list)) == 0:
                    return [{"errors":"twitter"+pl}]
                else:
                    return final_list

            #adding data to the list
            for status in decoded_data["statuses"]:
                #converting to lower case for ignoring case
                processed_search_val = (self.search_val).lower()
                processed_tweet_text = (status["text"]).lower()
                #replacing multiple spaces with single space
                processed_search_val = " ".join(processed_search_val.split())
                processed_tweet_text = " ".join(processed_tweet_text.split())
                if processed_search_val in processed_tweet_text:
                    final_list.append({"user_name":status["user"]["name"],"created_at":status["created_at"],"text":status["text"],"tweet_id":status["id"]})                       

            response_count = len(decoded_data["statuses"])
            tweets_found = len(final_list)

            request_count += 1                                                                                                   #LOG DATA

            #checking exit conditions
            if(response_count == 0):
                loop_condition = False
            else:
                if(response_count < 100):
                    loop_condition = False #we requested 100 tweets, if response is smaller there are no tweets to request
                if(tweets_found >= number_of_tweets):
                    final_list = final_list[0:number_of_tweets]
                    loop_condition = False
                else:
                    #setting up for the next iteration
                    twit_max_id = long(decoded_data["statuses"][-1]["id"])
                    twit_max_id -= 1

        logging.info("Requests Consumed: " + `request_count`)                                                                    #logging
        return final_list
