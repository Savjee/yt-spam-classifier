import os
import googleapiclient.discovery
from dotenv import load_dotenv
import google.oauth2.credentials
import google_auth_oauthlib.flow
from urllib import parse
import pickle
from typing import List

load_dotenv()

API_KEY = os.getenv("API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

CREDENTIAL_FILE = os.path.dirname(os.path.realpath(__file__)) + "/offline_credentials"
print(CREDENTIAL_FILE)

class Comment():
    def __init__(self, ytObj):
        rootObj = None

        if "topLevelComment" in ytObj["snippet"]:
            rootObj = ytObj["snippet"]["topLevelComment"]
        else:
            rootObj = ytObj

        self.id = rootObj["id"]
        self.publishedAt = rootObj["snippet"]["publishedAt"]
        self.textOriginal = rootObj["snippet"]["textOriginal"]
        self.authorName = rootObj["snippet"]["authorDisplayName"]
        self.likeCount = rootObj["snippet"]["likeCount"]

class CommentHelper():
    def __init__(self):
        #self.yt = googleapiclient.discovery.build(
        #    "youtube", "v3", developerKey = API_KEY
        #)
        self.authenticate()

    def authenticate(self):
        if os.path.isfile(CREDENTIAL_FILE):
            self.auth_from_file()
        else:
            self.auth_fetch_tokens()

    def auth_fetch_tokens(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                    'client_secret.json',
                    scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )
        flow.redirect_uri = 'http://localhost:8080/oauth2callback'

        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true'
        )

        print(authorization_url)
        raw_url = input("Redirect URL = ")
        code = parse.parse_qs(parse.urlparse(raw_url).query)["code"][0]
        print("code")
        flow.fetch_token(code=code)
        credentials = flow.credentials

        print("Token: %s, Refresh: %s" % (credentials.token, credentials.refresh_token))

        self.yt = googleapiclient.discovery.build(
                "youtube", "v3", credentials=credentials
        )

        print(credentials)
        with open(CREDENTIAL_FILE, "wb") as cred_file:
            pickle.dump(credentials, cred_file)

    def auth_from_file(self):
        with open(CREDENTIAL_FILE, "rb") as cred_file:
            credentials = pickle.load(cred_file)

            self.yt = googleapiclient.discovery.build(
                    "youtube", "v3", credentials=credentials
            )
    
    #
    # By default fetch only published comments
    #
    def fetch(self, next_page_token = None, moderation_status="published"):
        print("Fetching comments (next page token: %s, moderation status: %s)" 
                % (next_page_token, moderation_status))
        
        req = self.yt.commentThreads().list(
            part = "snippet,replies",
            maxResults = 100,
            pageToken = next_page_token,
            allThreadsRelatedToChannelId=CHANNEL_ID,
            moderationStatus=moderation_status,
            order="time"
        )
    
        res = req.execute()

        # Parse the comments into Comment objects
        comms = []
        for c in res["items"]:
            comms.append(Comment(c))
            if "replies" in c:
                print("has replies!")
                comms.extend(list(map(lambda com: Comment(com), c["replies"]["comments"])))

        return (comms, res["nextPageToken"]) 

    def markAsSpam(self, commentIds: List[str]):
        comIds = ",".join(commentIds)
        print("Marking as spam: %s" % (comIds))
        req = self.yt.comments().markAsSpam(
                id = comIds
        )

        res = req.execute()
        print(res)
        
        print("Marking as heldForReview")
        req2 = self.yt.comments().setModerationStatus(
                id=comIds,
                moderationStatus="heldForReview"
        )

        res2 = req2.execute()
        print(res2)

#ch = CommentHelper()
#ch.authenticate()
#ch.auth_from_file()
#ch.get_spam_comments()
#ch.markAsSpam("test")
