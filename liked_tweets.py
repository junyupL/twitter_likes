import requests
import os
import json
import time
import sys


# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2LikedTweetsPython"
    return r


def connect_to_endpoint(url, tweet_fields):
    response = requests.request(
        "GET", url, auth=bearer_oauth, params=tweet_fields)
    print(response.status_code)
    if response.status_code != 200:
        print(
            "Request returned an error: {} {}, Trying again later".format(
                response.status_code, response.text
            )
        )
        time.sleep(8 * 60)
        return connect_to_endpoint(url, tweet_fields)
    return response.json()


def main():    
    id = sys.argv[1]
    f = open("likesresult.json", "a")

    tweet_fields = "tweet.fields=author_id,created_at"
    url = "https://api.twitter.com/2/users/{}/liked_tweets".format(id)
    json_response = connect_to_endpoint(url, tweet_fields)
    all_data = json_response["data"]
    while "next_token" in json_response["meta"]:
        url = "https://api.twitter.com/2/users/{}/liked_tweets?pagination_token=".format(id) + json_response["meta"]["next_token"]
        json_response = connect_to_endpoint(url, tweet_fields)
        if "data" in json_response:
            all_data.extend(json_response["data"])

    names_and_usernames = {}
    author_ids = set()
    
    for tweet in all_data:
        author_ids.add(tweet["author_id"])
    first = True
    id_url = "https://api.twitter.com/2/users?ids="

    count = 0
    for auth_id in author_ids:   
        if first:
            id_url += auth_id
            first = False
        else:
            id_url += "," + auth_id
        count += 1
        if count == 100:
            names = connect_to_endpoint(id_url, "")
            
            id_url = "https://api.twitter.com/2/users?ids="
            count = 0
            first = True
            for name in names["data"]:
                names_and_usernames[name["id"]] = [name["name"], name["username"]]
    
    if count > 0:
        names = connect_to_endpoint(id_url, "")
        id_url = "https://api.twitter.com/2/users?ids="
        count = 0
        first = True
        for name in names["data"]:
            names_and_usernames[name["id"]] = [name["name"], name["username"]]

    for tweet in all_data:
        tweet["username"] = names_and_usernames[tweet["author_id"]][1] 
        tweet["name"] = names_and_usernames[tweet["author_id"]][0]
        
    f.write(json.dumps(all_data, indent=4))

    f.close()
        



if __name__ == "__main__":
    main()
