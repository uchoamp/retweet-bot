from requests_oauthlib import OAuth1Session
import json
import asyncio
import urllib
from firebase import conn, deleteRetweet, setRetweet
from datetime import datetime, timedelta, timezone

db = conn()


########################################################################
async def retweet(users, tweet_id, consumer_key, consumer_secret):
    await asyncio.sleep(0)
    now = datetime.now(timezone.utc)
    print(tweet_id)
    for key in list(users):
        access_token = users[key]["oauth_token"]
        access_token_secret = users[key]["oauth_token_secret"]

        url = "https://api.twitter.com/1.1/statuses/retweet/{}.json".format(
            tweet_id)
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        response = oauth.post(url)

        if response.status_code != 200:
            res_json = response.json()
            print("Request returned an error: {} {}".format(
                response.status_code, response.text))
            if res_json["errors"][0]["code"] == 144:
                return None

            users.pop(key)
        else:
            # print("Response code: {}".format(response.status_code))
            # json_response = response.json()
            # print(json.dumps(json_response, indent=4, sort_keys=True))
            print(f"@{key} retuitou, ID:{tweet_id}")

    if len(users) > 0:
        expire = now + timedelta(minutes=120)
        doc = {"expire": expire, "users": users}
        setRetweet(db, doc, tweet_id)

        asyncio.create_task(
            unretweet(users, tweet_id, consumer_key, consumer_secret))


async def unretweet(users, tweet_id, consumer_key, consumer_secret, wait=7200):
    await asyncio.sleep(wait)
    for key in users:
        access_token = users[key]["oauth_token"]
        access_token_secret = users[key]["oauth_token_secret"]

        url = "https://api.twitter.com/1.1/statuses/unretweet/{}.json".format(
            tweet_id)
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        response = oauth.post(url)

        if response.status_code != 200:
            res_json = response.json()
            print("Request returned an error: {} {}".format(
                response.status_code, response.text))
            if res_json["errors"][0]["code"] == 144:
                return None
        # print("Response code: {}".format(response.status_code))
        # json_response = response.json()
        # print(json.dumps(json_response, indent=4, sort_keys=True))
        print("Retuite removido, ID:%s" % tweet_id)
    deleteRetweet(db, tweet_id)


########################################################################


async def like(users, tweet_id, consumer_key, consumer_secret):
    await asyncio.sleep(0)

    for key in users:
        access_token = users[key]["oauth_token"]
        access_token_secret = users[key]["oauth_token_secret"]

        url = "https://api.twitter.com/1.1/favorites/create.json?id={}".format(
            tweet_id)
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        response = oauth.post(url)

        if response.status_code != 200:
            raise Exception("Request returned an error: {} {}".format(
                response.status_code, response.text))

        # print("Response code: {}".format(response.status_code))
        # json_response = response.json()
        # print(json.dumps(json_response, indent=4, sort_keys=True))
        print("Tweet curtido, ID:%s" % tweet_id)


###########################################################################


def tweet(users, content, consumer_key, consumer_secret):
    content = urllib.parse.quote_plus(content)
    for key in users:
        access_token = users[key]["oauth_token"]
        access_token_secret = users[key]["oauth_token_secret"]

        url = "https://api.twitter.com/1.1/statuses/update.json?status={}".format(
            content)
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        response = oauth.post(url)

        if response.status_code != 200:
            raise Exception("Request returned an error: {} {}".format(
                response.status_code, response.text))

        print("Response code: {}".format(response.status_code))
        # json_response = response.json()
        # print(json.dumps(json_response, indent=4, sort_keys=True))
        print("Tweet postado")


def follow(users, username, consumer_key, consumer_secret):

    for key in users:
        access_token = users[key]["oauth_token"]
        access_token_secret = users[key]["oauth_token_secret"]

        url = "https://api.twitter.com/1.1/friendships/create.json?screen_name={}".format(
            username)
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        response = oauth.post(url)
        json_response = response.json()
        if response.status_code != 200:
            # print("Request returned an error: {} {}".format(response.status_code, response.text))
            if (json_response["errors"][0]["code"] == 108
                    or json_response["errors"][0]["code"] == 32):
                print(f"Conta @{username} não existe.")
                break

            continue

        # print(json.dumps(json_response, indent=4, sort_keys=True))
        # print("Response code: {}".format(response.status_code))
        print("@%s seguiu @%s." % (key, username))
