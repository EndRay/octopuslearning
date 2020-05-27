import urllib.request
import json

import rating_calculator


def get_contests():
    url = 'https://codeforces.com/api/contest.list'
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    return json.loads(r.decode('utf-8'))['result']


def get_user_status(handle):
    url = f'https://codeforces.com/api/user.status?handle={handle}'
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    return json.loads(r.decode('utf-8'))['result']


def get_contest_standings(contest_id, show_unofficial=False):
    url = f'https://codeforces.com/api/contest.standings?contestId={contest_id}&showUnofficial={show_unofficial}'
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    res = json.loads(r.decode('utf-8'))
    return res["result"]


def get_contest_rating_changes(contest_id):
    url = f'https://codeforces.com/api/contest.ratingChanges?contestId={contest_id}'
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    res = json.loads(r.decode('utf-8'))
    return res["result"]


def calculate_rating_delta(contest_id, other_users):
    handles = map(lambda x: x[0], other_users)
    try:
        standings = get_contest_standings(contest_id, True)
        rating_changes = get_contest_rating_changes(contest_id)
    except:
        return None
    if not standings or not rating_changes:
        return None
    standings = standings["rows"]
    points = {}
    for contestant in standings:
        if len(contestant["party"]["members"]) == 1:
            points[contestant["party"]["members"][0]["handle"]] = contestant["points"]
    users = []
    for contestant in rating_changes:
        if contestant["handle"] not in handles:
            users.append((contestant["handle"], points[contestant["handle"]], 0, contestant["oldRating"]))
    for user in other_users:
        handle = user[0]
        rating = user[1]
        users.append((handle, points[handle], 0, rating))

    calculator = rating_calculator.CodeforcesRatingCalculator(users)
    return calculator.calculate_rating_changes()


def main():
    current_rating = 1500
    handle = "EndRay"
    user_status = get_user_status(handle)
    contests = []
    for submission in user_status:
        if submission['author']['participantType'] in ["CONTESTANT", "VIRTUAL", "OUT_OF_COMPETITION"]:
            contests.append((submission['author']['startTimeSeconds'], submission['author']['contestId'],
                             submission['author']['participantType']))
    contests = list(set(contests))
    contests.sort()

    data_f = open("static/data.js", "w")
    data_f.write("graph_data = ")

    data = []

    for start_time_seconds, contest_id, participant_type in contests[:5]:
        delta = calculate_rating_delta(contest_id, [(handle, current_rating)])
        if delta is None:
            continue
        new_rating = current_rating + delta[handle]
        print(current_rating, "->", new_rating)
        current_rating = new_rating
        data.append({"x": start_time_seconds, "y": new_rating})

    data_f.write(json.dumps(data))
    data_f.close()


main()
