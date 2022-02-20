import os

if os.environ.get("PYTHON_ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

config_twitter_api = {
    "BEARER_TOKEN": os.environ.get("BEARER_TOKEN"),
    "CONSUMER_KEY": os.environ.get("CONSUMER_KEY"),
    "CONSUMER_SECRET": os.environ.get("CONSUMER_SECRET"),
}
