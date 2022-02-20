import asyncio
import json
from datetime import datetime, timedelta, timezone

import requests
from actions import db, retweet, unretweet, like
from firebase import setUser, getUsers, getRetweeteds, getRetweets

from config import config_twitter_api


def canRetweet(standby):
    now = datetime.now(timezone.utc)

    if now > standby:
        return True
    return False


def allRetweeteds():
    rule = []
    users = getUsers(db, w=2)
    retweeteds = getRetweeteds(db, w=1)

    for username in users:
        rule.append("from:" + username)
    for username in retweeteds:
        rule.append("from:" + username)

    return " OR ".join(rule)


def auth():
    consumer_key = config_twitter_api.get("CONSUMER_KEY")
    consumer_secret = config_twitter_api.get("CONSUMER_SECRET")
    return consumer_key, consumer_secret


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers)
    if response.status_code != 200:
        raise Exception("Cannot get rules (HTTP {}): {}".format(
            response.status_code, response.text))
    # print(json.dumps(response.json()))
    return response.json()


def get_params():
    return {"expansions": "author_id", "user.fields": "id,name,username"}


def delete_all_rules(headers, bearer_token, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))

    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload)
    if response.status_code != 200:
        raise Exception("Cannot delete rules (HTTP {}): {}".format(
            response.status_code, response.text))
    # print(json.dumps(response.json()))
    # print("Rule is clear.")


def set_rules(headers, bearer_token, retweeteds):
    if retweeteds != "":
        # You can adjust the rules if needed
        sample_rules = [{"value": f"({retweeteds}) -is:retweet -is:reply"}]
        payload = {"add": sample_rules}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            headers=headers,
            json=payload,
        )
        if response.status_code != 201:
            print("Cannot add rules (HTTP {}): {}".format(
                response.status_code, response.text))
            print("Não foi possivel aplica alterações.")
            return False
        json_response = response.json()
        # print(json.dumps(json_response, indent=4))
        rule = json_response["data"][0]["value"]
        # print(f"Regra: {rule}")
        # print("adicionada.")

        return rule


async def checkRetweets(consumer_key, consumer_secret):
    retweets = getRetweets(db)

    now = datetime.now(timezone.utc)
    for retweet_id in retweets:
        expire = retweets[retweet_id]["expire"]
        users = retweets[retweet_id]["users"]

        delta = expire - now
        delta_sec = delta.total_seconds()
        delta_sec = round(delta_sec)

        if delta_sec <= 0:
            delta_sec = 0

        asyncio.create_task(
            unretweet(users,
                      retweet_id,
                      consumer_key,
                      consumer_secret,
                      wait=delta_sec))


async def get_stream(headers, bearer_token, params):
    consumer_key, consumer_secret = auth()

    asyncio.create_task(checkRetweets(consumer_key, consumer_secret))

    wait = 60

    while True:
        await asyncio.sleep(wait)
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream",
            headers=headers,
            params=params,
            stream=True,
        )
        print(response.status_code)
        print("x-rate-limit-limit:{}\nx-rate-limit-remaining:{}\n\
x-rate-limit-reset:{}".format(response.headers["x-rate-limit-limit"],
                              response.headers["x-rate-limit-remaining"],
                              response.headers["x-rate-limit-reset"]))

        if response.status_code != 200:
            print("Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text))
            wait *= 2
        else:
            for response_line in response.iter_lines():
                if response_line:
                    json_response = json.loads(response_line)
                    if "data" in json_response:
                        print(
                            json.dumps(json_response, indent=4,
                                       sort_keys=True))
                        username = json_response["includes"]["users"][0][
                            "username"]
                        users = getUsers(db, w=1)
                        now = datetime.now(timezone.utc)

                        if username in users:
                            standby = now + timedelta(minutes=240)
                            users[username]["standby"] = standby
                            setUser(db, users[username], username)
                            users.pop(username)

                        for username in list(users):
                            standby = users[username]["standby"]
                            if not canRetweet(standby):
                                users.pop(username)

                        if len(users) > 0:
                            tweet_id = json_response['data']['id']

                            asyncio.create_task(
                                retweet(users, tweet_id, consumer_key,
                                        consumer_secret))
                            asyncio.create_task(
                                like(users, tweet_id, consumer_key,
                                     consumer_secret))
                            pass
                        print("Next")
                    else:
                        print(
                            json.dumps(json_response, indent=4,
                                       sort_keys=True))
                        break

                await asyncio.sleep(0)
            wait = 60
        response.close()


def main():
    bearer_token = config_twitter_api["BEARER_TOKEN"]
    retweeteds = allRetweeteds()
    headers = create_headers(bearer_token)
    rules = get_rules(headers, bearer_token)
    delete_all_rules(headers, bearer_token, rules)
    new_rules = set_rules(headers, bearer_token, retweeteds)

    print(new_rules)
    params = get_params()

    asyncio.run(get_stream(headers, bearer_token, params))


if __name__ == "__main__":
    main()
