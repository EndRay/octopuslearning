import urllib.request
import json
from datetime import datetime

import rating_calculator
import rating_system


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


def main():
    current_rating = 1500
    handle = "EndRay"
    user_status = get_user_status(handle)
    contests = []
    for submission in user_status:
        if submission['author']['participantType'] in ["CONTESTANT"]:
            contests.append((submission['author']['startTimeSeconds'], submission['author']['contestId'],
                             submission['author']['participantType']))
    contests = list(set(contests))
    contests.sort()
    for startTimeSeconds, contestId, participantType in contests:
        try:
            standings = get_contest_standings(contestId, True)
            rating_changes = get_contest_rating_changes(contestId)
        except:
            continue
        if not standings or not rating_changes:
            continue
        standings = standings["rows"]
        points = {}
        for contestant in standings:
            if len(contestant["party"]["members"]) == 1:
                points[contestant["party"]["members"][0]["handle"]] = contestant["points"]
        users = []
        for contestant in rating_changes:
            if contestant["handle"] != handle:
                users.append((contestant["handle"], points[contestant["handle"]], 0, contestant["oldRating"]))
        users.append((handle, points[handle], 0, current_rating))

        calculator = rating_calculator.CodeforcesRatingCalculator(users)
        new_rating = current_rating + calculator.calculate_rating_changes()[handle]
        print(current_rating, "->", new_rating)
        current_rating = new_rating

    print(contests)


main()
