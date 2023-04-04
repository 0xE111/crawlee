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

For more options, run
```sh
python src/main.py --help
```
