# Crawlee

This is a simple script to parse public articles / images from websites with user content.

Currently only Telegra.ph is supported.

## Telegra.ph

The search is performed by checking user notes with the title you request. For example, if you request "test", the script will probe pages "telegra.ph/test-01-01", "telegra.ph/test-02-01" etc.

# How to run

```sh
git clone https://github.com/c0ntribut0r/crawlee.git
cd crawlee
python -m venv venv
source venv/bin/activate
pip install --upgrade pip -r requirements.txt
python src/main.py "funny story"
```
Output:
```
1 Funny story
https://telegra.ph/funny-story-08-25

Funny story 
policemen in action August 25, 2017 
Funny story policemen in action Policemen are in action.  They want to arrest the most dangerous smuggler in Scarborough. t 
Edit Publish 

------------------------------
2 Funny story
https://telegra.ph/funny-story-11-22

Funny story 
Pun November 22, 2016 
Funny story Pun Hey! Glad to see Telegraph. Interesting.. Flickr Hoho 
Edit Publish 

```

For more options, run
```sh
python src/main.py --help
```

# As telegram bot

```sh
python src/bot.py
```

<img src="https://user-images.githubusercontent.com/11032969/229802551-eadfdd18-1fec-4293-b3a1-0b9b470470de.jpg" width="400">
