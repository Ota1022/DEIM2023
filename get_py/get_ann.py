import csv
import datetime
import time

import dateutil.parser
import requests


def auth():
    return "AAAAAAAAAAAAAAAAAAAAAAovSgEAAAAAWd%2FAlCy9ReVbZdrwU96tcpAKy%2BY%3DqRLVMIE27Rz8AoBM3GgfNlrlSXyEIzvuKf4FEWMMDxwVLSugvc"


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def create_url(keyword, start_date, end_date, max_results=10):
    search_url = "https://api.twitter.com/2/tweets/search/all"
    query_params = {
        "query": keyword,
        "start_time": start_date,
        "end_time": end_date,
        "max_results": max_results,
        "expansions": "author_id",
        "tweet.fields": "created_at,public_metrics",
        "next_token": {},
    }
    return (search_url, query_params)


def connect_to_endpoint(url, headers, params, next_token=None):
    params["next_token"] = next_token
    response = requests.request("GET", url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def append_to_csv(json_response, fileName):
    JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    csvFile = open(fileName, "a", newline="", encoding="utf-8")
    csvWriter = csv.writer(csvFile)
    for i in range(len(json_response["data"])):
        c_a = json_response["data"][i]["created_at"]
        created_at = dateutil.parser.parse(
            c_a).astimezone(JST).replace(tzinfo=None)
        text = json_response["data"][i]["text"].replace("\n", " ")
        tweet_id = json_response["data"][i]["id"]
        author_id = json_response["data"][i]["author_id"]
        retweet_count = json_response["data"][i]['public_metrics']['retweet_count']
        like_count = json_response["data"][i]['public_metrics']['like_count']
        for i, d in enumerate(json_response["includes"]["users"]):
            if d["id"] == author_id:
                username = json_response["includes"]["users"][i]["username"]
        res = [created_at, tweet_id, text, author_id,
               username, like_count, retweet_count]
        csvWriter.writerow(res)
    csvFile.close()


def main():
    bearer_token = auth()
    headers = create_headers(bearer_token)
    # keyword = "#cnann -is:retweet"
    # keyword = "#星野源ANN -is:retweet"
    # keyword = "#乃木坂46ANN -is:retweet"
    # keyword = "#ナインティナインANN -is:retweet"
    # keyword = "#霜降り明星ANN -is:ret
    keyword = "#annkw -is:retweet"
    start_date = "2022-02-12T16:00:00.000Z"
    end_date = "2022-02-12T18:05:00.000Z"
    max_results = 200
    total_tweets = 0

    url = create_url(keyword, start_date, end_date, max_results)
    json_response = connect_to_endpoint(url[0], headers, url[1])

    dt_now = datetime.datetime.now()
    fileName = "tweet" + str(dt_now.strftime("%y%m%d_%H%M%S")) + ".csv"
    csvFile = open(fileName, "a", newline="", encoding="utf-8")
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(["created_at", "tweet_id", "text", "author_id",
                       "username", "like_count", "retweet_count"])
    csvFile.close()

    count = 0
    flag = True
    next_token = None

    while flag:
        print("Token: ", next_token)
        url = create_url(keyword, start_date, end_date, max_results)
        json_response = connect_to_endpoint(
            url[0], headers, url[1], next_token)
        result_count = json_response["meta"]["result_count"]

        if "next_token" in json_response["meta"]:
            next_token = json_response["meta"]["next_token"]
            print("Next Token: ", next_token)
            if result_count is not None and result_count > 0 and next_token is not None:
                append_to_csv(json_response, "tweet" +
                              str(dt_now.strftime("%y%m%d_%H%M%S")) + ".csv")
                count += result_count
                total_tweets += result_count
                print("Total # of Tweets added: ", total_tweets)
                print("-------------------")
        else:
            if result_count is not None and result_count > 0:
                print("-------------------")
                append_to_csv(json_response, "tweet" +
                              str(dt_now.strftime("%y%m%d_%H%M%S")) + ".csv")
                count += result_count
                total_tweets += result_count
                print("Total # of Tweets added: ", total_tweets)
                print("-------------------")
                break

            flag = False
            next_token = None
        time.sleep(1)

    print("Total number of results: ", total_tweets)


if __name__ == '__main__':
    main()
