import os
import jinja2
import webapp2
from twitterhandler import TwitterHandler
from datastorehandler import RecordHandler as Records

path = os.path.join(os.path.dirname(__file__), "templates/") 

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(path),
    extensions=["jinja2.ext.autoescape"],
    autoescape=True)

class HomePage(webapp2.RequestHandler):
    def get(self):
        template_values = {"searches":Records.returnSearchList()}
        template = JINJA_ENVIRONMENT.get_template("homepage.html")
        self.response.out.write(template.render(template_values))

class DisplayTweets(webapp2.RequestHandler):
    def get(self):
        self.redirect("/")
    def post(self):
        query = self.request.get("query")
        source = self.request.get("source")

        tweets = None
        index = -1

        recordlist = list()
        if Records.searchKeyListContains(query):
            Records.updateSearchKeyPosition(query)
            recordlist.extend(Records.getRecordsTimeListFor(query))
        else:
            Records.addSearchKey(query)
            Records.updateTweetbase()

        if source == "search-bar" or source == "history-bar-home":
            twitter_handler = TwitterHandler(query)
            tweets = twitter_handler.retrieveData()
            #write code for error condition
        else:
            index = int(self.request.get("index"))
            tweets = Records.getRecordsByIndexFor(query, index)

        template_values = {
                           "query"  : query,
                           "records": recordlist,
                           "disable": index,
                           "tweets" : reversed(tweets),
                           "t_count": len(tweets)
                          }
        template = JINJA_ENVIRONMENT.get_template("tweetspage.html")
        self.response.write(template.render(template_values))

class UpdateTweetbase(webapp2.RequestHandler):
    def get(self):
        Records.updateTweetbase()
        

app = webapp2.WSGIApplication([
    ("/", HomePage),
    ("/tweets", DisplayTweets),
    ("/scanupdate", UpdateTweetbase)
], debug=True)
