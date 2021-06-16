import os
import sys
import csv
import time

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from helpers import CommentHelper

def write_to_csv(comments):
    with open("comments.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
       
        for com in comments:
            writer.writerow([
                com.id,
                com.publishedAt,
                com.textOriginal,
                com.authorName,
                com.likeCount,
            ])
            
if __name__ == "__main__":
    ch = CommentHelper.CommentHelper()
    comments = []
    nextPageToken = None

    while True:
        (comments, nextPageToken) = ch.fetch(next_page_token = nextPageToken)
        write_to_csv(comments)

        if nextPageToken is None:
            break

        time.sleep(0.25)
