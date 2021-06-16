import sys
import os.path
import tensorflow as tf
import tensorflow_hub as hub
import time
import datetime
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from helpers import CommentHelper

##
# This script runs periodically. It fetches new comments from YouTube,
# runs them through the trained model and marks comments as spam
# when needed.
##

print("Loading model")
model = tf.keras.models.load_model('./trained-model.h5', custom_objects={'KerasLayer':hub.KerasLayer})
model.summary()

print("Fetching latest comments")
ch = CommentHelper.CommentHelper()
ch.authenticate()

nextPageToken = None


# 
today = datetime.datetime.now()
twodays = datetime.timedelta(days = 2)
mindate = (today - twodays).isoformat()

loop = True

while loop:
    (comments, nextPageToken) = ch.fetch(next_page_token = nextPageToken)
    spam = []

    for com in comments:
        if com.publishedAt < mindate:
            print("Comment was posted over 2 days ago. Stopping!")
            loop = False
            break

        res = model.predict([com.textOriginal])
       
        if res > 0.1:
            if input("mark as spam? [y/n] %s" % (com.textOriginal)) == "y":
                spam.append(com.id)
   
    # report them in 1 go
    if len(spam) > 0:
        print("Have %d comments, reporting as spam" % (len(spam)))
        ch.markAsSpam(spam)
        spam = []
        

    if nextPageToken is None:
        break
    
    time.sleep(0.25)


