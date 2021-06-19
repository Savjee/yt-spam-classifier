import sys
import os.path
import tensorflow as tf
import tensorflow_hub as hub
import time
import datetime
import gspread
import itertools

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from helpers import CommentHelper

print("Fetching commentIds in Google Sheet")
cred_path = os.path.dirname(os.path.abspath(__file__))
gc = gspread.service_account(filename=cred_path + "/yt-spam-filter-013e7aa5ffc1.json")
sh = gc.open_by_key("1QEQrLne1SDxwQVl5qpGQokEKG4FNZqX6kMuFMmAyeWg")
worksheet = sh.get_worksheet(0)
commentsInSheet = worksheet.get("A:A")
commentsInSheet = list(itertools.chain.from_iterable(commentsInSheet))

print("Comments in sheet: %d" % (len(commentsInSheet)))

print("Loading model")
model = tf.keras.models.load_model('./trained-model.h5', custom_objects={'KerasLayer':hub.KerasLayer})
model.summary()

print("Fetching latest comments")
ch = CommentHelper.CommentHelper()
ch.authenticate()

nextPageToken = None

today = datetime.datetime.now()
timespan = datetime.timedelta(days = 7)
mindate = (today - timespan).isoformat()

loop = True

while loop:
    (comments, nextPageToken) = ch.fetch(next_page_token = nextPageToken)
    spam = []
    allComs = []

    for com in comments:
        if com.publishedAt < mindate:
            print("Comment was posted before timewindow. Stopping!")
            loop = False
            break

        res = float(model.predict([com.textOriginal]))
        
        if com.id not in commentsInSheet:
            allComs.append((com, res))

        if res > 0.8:
            #if input("mark as spam? [y/n] %s" % (com.textOriginal)) == "y":
            spam.append(com.id)

    # Add them all to Google Sheets
    worksheet.append_rows(
        list(map(lambda c: [
            c[0].id, 
            c[0].publishedAt, 
            c[0].textOriginal, 
            c[0].authorName, 
            c[0].likeCount, 
            "", # Manual spam rating
            c[1] # Inference result
        ], allComs))
    )

    # Reset list before we continue
    allComms = []

    # report them in 1 go
    if len(spam) > 0:
        print("Have %d comments, reporting as spam" % (len(spam)))
        ch.markAsSpam(spam)
        spam = []
        

    if nextPageToken is None:
        break
    
    time.sleep(0.25)


