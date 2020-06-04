from codeforces.api import get_user_status, get_user_performance, get_contest_standings, get_contest_rating_changes
from codeforces.db import *

from codeforces.rating_system import rating_calculator

def read_contest(contest_id, refresh=False):
    session = Session()
    if refresh:
        session.query(Performance).filter(Performance.contestId == contest_id).delete(synchronize_session=False)
        session.query(Contest).filter(Contest.contestId == contest_id).delete(synchronize_session=False)
        session.commit()
    if session.query(Contest.isBroken).filter(Contest.contestId == contest_id).scalar():
        return False
    if session.query(Performance).filter(Performance.contestId == contest_id).first() is not None:
        return True
    contest = Contest()
    contest.contestId = contest_id
    contest.isBroken = True
    contest.name = None
    contest.durationSeconds = None
    contest.startTimeSeconds = None
    try:
        standings = get_contest_standings(contest_id, True)
        rating_changes = get_contest_rating_changes(contest_id)
    except:
        session.add(contest)
        session.commit()
        return False
    if not standings or not rating_changes:
        session.add(contest)
        session.commit()
        return False
    contest.name = standings["contest"]["name"]
    contest.durationSeconds = standings["contest"]["durationSeconds"]
    contest.startTimeSeconds = standings["contest"]["startTimeSeconds"]
    standings = standings["rows"]
    for contestant in standings:
        if contestant["party"]["participantType"] == "CONTESTANT" and len(contestant["party"]["members"]) > 1:
            session.add(contest)
            session.commit()
            return False
    contest.isBroken = False
    session.add(contest)
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
    session.bulk_save_objects(performances.values())
    session.commit()
    return True


def calculate_rating_delta(contest_id, handle, rating, recalculate=False):
    session = Session()
    query = session.query(Delta.delta).filter(
        Delta.contestId == contest_id and Delta.handle == handle and Delta.oldRating == rating)
    if recalculate:
        query.delete(synchronize_session=False)
        session.commit()
    elif query.scalar() is not None:
        return True
    if not read_contest(contest_id):
        return False
    users = session.query(Performance.handle, Performance.points, Performance.penalty, Performance.oldRating) \
        .filter(Performance.contestId == contest_id).filter(Performance.oldRating != None).all()
    for i in range(len(users)):
        if users[i][0] == handle:
            users.pop(i)
            break
    user_standings = get_user_performance(contest_id, handle)["rows"]
    performance = (0, {})
    for contestant in user_standings:
        if contestant["party"]["participantType"] in ["CONTESTANT", "VIRTUAL", "OUT_OF_COMPETITION"] and \
                contestant["party"]["startTimeSeconds"] > performance[0]:
            performance = (contestant["party"]["startTimeSeconds"], contestant)
    points, penalty = performance[1]["points"], performance[1]["penalty"]
    users.append((handle, points, penalty, rating))
    calculator = rating_calculator.CodeforcesRatingCalculator(users)
    delta = Delta()
    delta.contestId = contest_id
    delta.handle = handle
    delta.oldRating = rating
    delta.delta = calculator.calculate_rating_changes()[handle]
    session.add(delta)
    session.commit()
    return True


def calculate(handle):
    current_rating = 1500
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
        if not calculate_rating_delta(contest_id, handle, current_rating):
            continue
        session = Session()
        delta = session.query(Delta.delta).filter(
            Delta.contestId == contest_id and Delta.handle == handle and Delta.oldRating == current_rating).scalar()
        new_rating = current_rating + delta
        # print(f'{datetime.fromtimestamp(start_time_seconds)}\t:  {current_rating} -> {new_rating}')
        current_rating = new_rating
        data.append({"x": start_time_seconds, "y": new_rating, "delta": delta, "contest": session.query(Contest.name) \
                    .filter(Contest.contestId == contest_id).one()})
    return data
