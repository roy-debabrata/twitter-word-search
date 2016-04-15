from google.appengine.ext import ndb
from twitterhandler import TwitterHandler
from datetime import datetime
from datetime import timedelta

SEARCH_QUERY_LIST_NAME = "search_query_list"
RECORD_KEY_PREFIX = "record_key_"
MAX_TWEETS_IN_A_SEARCH = 500
MAX_SEARCH_LIST_SIZE = 30
SEARCH_REPEAT_TIME_MINS = 60

class SearchKey(ndb.Model):
    search_query = ndb.StringProperty(indexed = False)
    search_time = ndb.DateTimeProperty(auto_now_add = True)
    next_search_time = ndb.DateTimeProperty(indexed = False, auto_now_add = True)

    @classmethod
    def getsearchlist(cls, search_key):
        return cls.query(ancestor=search_key).order(-cls.search_time)

class SearchResult(ndb.Model):
    search_time = ndb.DateTimeProperty(auto_now_add=True)
    search_result = ndb.JsonProperty(indexed = False)

class SearchRecord(ndb.Model):
    search_query = ndb.StringProperty(indexed = False)
    num_of_result = ndb.IntegerProperty(indexed = False)
    search_result = ndb.StructuredProperty(SearchResult, repeated=True)

    @classmethod
    def getsearchrecord(cls, record_key):
        return cls.query(ancestor=record_key)

class RecordHandler:
    "Contains function that deal with datastore"
    @classmethod
    def addSearchKey(cls, search_query):
        if cls.searchKeyListContains(search_query):
            cls.updateSearchKeyPosition(search_query)
        else:
            search_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME)
            searches = SearchKey.getsearchlist(search_key).fetch(MAX_SEARCH_LIST_SIZE)

            if len(searches) == MAX_SEARCH_LIST_SIZE:
                #Removing searchkey from the list
                last_search_query = searches[-1].search_query
                searches[-1].key.delete()
                #Removing searchrecord from the list. We could retain this but that's a choice.
                record_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME, "record_list", RECORD_KEY_PREFIX + normalize(last_search_query))
                record = SearchRecord.getsearchrecord(record_key).get()
                record.key.delete()
            searchinfo = SearchKey(parent = search_key)
            searchinfo.search_query = search_query
            searchinfo.put()
            new_record_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME, "record_list", RECORD_KEY_PREFIX + normalize(search_query))
            new_record = SearchRecord(parent = new_record_key)
            new_record.search_query = search_query
            new_record.num_of_result = 0
            new_record.put()

    @classmethod
    def returnSearchList(cls):
        search_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME)
        searches = SearchKey.getsearchlist(search_key).fetch(MAX_SEARCH_LIST_SIZE)

        search_list = list()
        for search in searches:
            search_list.append(search.search_query)

        return search_list

    @classmethod
    def searchKeyListContains(cls, search_query):
        search_list = cls.returnSearchList()

        for item in search_list:
            if normalize(item) == normalize(search_query):
                return True
        return False

    @classmethod
    def updateSearchKeyPosition(cls, search_query):
        search_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME)
        searches = SearchKey.getsearchlist(search_key).fetch(MAX_SEARCH_LIST_SIZE)

        for search in searches:
            if normalize(search.search_query) == normalize(search_query):
                search.search_time = datetime.now()
                search.put()
                break

    @classmethod
    def getRecordsTimeListFor(cls, search_query):
        new_record_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME, "record_list", RECORD_KEY_PREFIX + normalize(search_query))
        record = SearchRecord.getsearchrecord(new_record_key).get()

        if record.num_of_result == 0:
            return list()
        timeList = list()
        for record_data in record.search_result:
            timeList.append(record_data.search_time)
        return timeList

    @classmethod
    def getRecordsByIndexFor(cls, search_query, index):
        new_record_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME, "record_list", RECORD_KEY_PREFIX + normalize(search_query))
        record = SearchRecord.getsearchrecord(new_record_key).get()

        if record.num_of_result > index:
            return record.search_result[index].search_result
        else:
            return list()

    @classmethod
    def updateTweetbase(cls):
        search_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME)
        searches = SearchKey.getsearchlist(search_key).fetch(MAX_SEARCH_LIST_SIZE)

        for search in searches:
            if search.next_search_time <= datetime.now():
                #we update the search record
                new_record_key = ndb.Key("search_query_list", SEARCH_QUERY_LIST_NAME, "record_list", RECORD_KEY_PREFIX + normalize(search.search_query))
                record = SearchRecord.getsearchrecord(new_record_key).get()
                
                since_id = long(-1)
                for record_s in reversed(record.search_result):
                    if len(record_s.search_result) > 0 :
                        since_id = long(record_s.search_result[0]["tweet_id"])
                        break

                twitter_handler = TwitterHandler(search.search_query, since_id)
                tweets = twitter_handler.retrieveData(MAX_TWEETS_IN_A_SEARCH)

                if record.num_of_result == 0:
                    record.search_result = [SearchResult(search_result = tweets)]
                else:
                    record.search_result.append(SearchResult(search_result = tweets))

                record.num_of_result += 1
                record.put()

                #we update the list of searches
                search.next_search_time = search.next_search_time + timedelta(minutes = SEARCH_REPEAT_TIME_MINS)
                search.put()

def normalize(value):
    value = value.lower()
    return "_".join(value.split())
