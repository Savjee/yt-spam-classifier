# yt-spam-filter

Using TensorFlow to automatically filter crypto-related spam comments on YouTube.
🎬 See my video for more details: [https://youtu.be/zSEYC3CCA1I](https://youtu.be/zSEYC3CCA1I)

## Repository structure

* `00-CoreML test` -> First test with Apple's CoreML.
* `01-fetch-input-data` -> Python script that fetches comments from YouTube and stores them in a CSV file
* `02-rated-comments` -> Dataset of comments from my channel, marked as spam (1) or not spam (0)
* `03-tensorflow-training` -> Jupyter notebook used to train the text classifier with TensorFlow
* `04-inference` -> Python script that runs periodically to filter latest comments on my channel


## Installation
Clone this repo:
```
git clone https://github.com/Savjee/yt-spam-classifier.git
```

Install dependencies (might not be complete):
```
pip3 install -r requirements.txt
```

Create a `.env` file from the template, and fill in your YouTube API key and Channel ID
```
cp .env.dist .env
```

More instructions to follow.

## Contribute
Feel free to fork or submit improvements but be gentle. This is my first ML and Python project (it probably shows).
