import urllib.request
import json
from datetime import datetime
from base import *

import rating_calculator

BASE = 'https://codeforces.com'


# BASE = 'http://127.0.0.1:8080'

def get_contests():
    url = f'{BASE}/api/contest.list'
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    return json.loads(r.decode('utf-8'))['result']


def get_user_status(handle):
    url = f'{BASE}/api/user.status?handle={handle}'
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    return json.loads(r.decode('utf-8'))['result']


def get_contest_standings(contest_id, show_unofficial=False):
    url = f'{BASE}/api/contest.standings?contestId={contest_id}&showUnofficial={show_unofficial}'
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    res = json.loads(r.decode('utf-8'))
    return res["result"]


def get_contest_rating_changes(contest_id):
    url = f'{BASE}/api/contest.ratingChanges?contestId={contest_id}'
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    res = json.loads(r.decode('utf-8'))
    return res["result"]


def read_contest(contest_id):
    if len(session.query(Performance).filter(Performance.contestId == contest_id).all()) != 0:
        return True
    try:
        standings = get_contest_standings(contest_id, True)
        rating_changes = get_contest_rating_changes(contest_id)
    except:
        return False
    if not standings or not rating_changes:
        return False
    contest_name = standings["contest"]["name"]
    contest_duration = standings["contest"]["name"]
    standings = standings["rows"]
    for contestant in standings:
        if contestant["party"]["participantType"] == "CONTESTANT" and len(contestant["party"]["members"]) > 1:
            return False
    performances = {}
    for contestant in standings:
        if contestant["party"]["participantType"] in ["CONTESTANT", "VIRTUAL", "OUT_OF_COMPETITION"]:
            for member in contestant["party"]["members"]:
                handle = member["handle"]
                performances[handle] = Performance()
                performances[handle].contestId = contest_id
                performances[handle].handle = handle
                performances[handle].points = contestant["points"]
                performances[handle].penalty = contestant["penalty"] if "penalty" in contestant.keys() else 0
                performances[handle].oldRating = None
    for contestant in rating_changes:
        performances[contestant["handle"]].oldRating = contestant["oldRating"]
    for performance in performances.values():
        session.add(performance)
    session.commit()
    return True


def calculate_rating_delta(contest_id, other_users):
    if not read_contest(contest_id):
        return None
    handles = map(lambda x: x[0], other_users)
    users = session.query(Performance.handle, Performance.points, Performance.penalty, Performance.oldRating) \
        .filter(Performance.contestId == contest_id).filter(Performance.oldRating != None).all()
    for user in other_users:
        handle = user[0]
        rating = user[1]
        points, penalty = session.query(Performance.points, Performance.penalty)\
            .filter(Performance.contestId == contest_id).filter(Performance.handle == handle).all()[0]
        users.append((handle, points, penalty, rating))
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

    data = []

    for start_time_seconds, contest_id, participant_type in contests:
        delta = calculate_rating_delta(contest_id, [(handle, current_rating)])
        if delta is None:
            continue
        new_rating = current_rating + delta[handle]
        print(f'{datetime.fromtimestamp(start_time_seconds)}\t:  {current_rating} -> {new_rating}')
        current_rating = new_rating
        data.append({"x": start_time_seconds, "y": new_rating})

    data_f = open(f"static/{handle}", "w")
    data_f.write(json.dumps(data))
    data_f.close()


main()
