import urllib.request
import json

BASE = 'https://codeforces.com'

def get_by_url(url):
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req).read()
    return json.loads(r.decode('utf-8'))['result']


def get_contests():
    return get_by_url(f'{BASE}/api/contest.list')


def get_user_status(handle):
    return get_by_url(f'{BASE}/api/user.status?handle={handle}')


def get_contest_standings(contest_id, show_unofficial=False):
    return get_by_url(f'{BASE}/api/contest.standings?contestId={contest_id}&showUnofficial={show_unofficial}')


def get_contest_rating_changes(contest_id):
    return get_by_url(f'{BASE}/api/contest.ratingChanges?contestId={contest_id}')


def get_user_performance(contest_id, handle, show_unofficial=True):
    return get_by_url(
        f'{BASE}/api/contest.standings?contestId={contest_id}&handles={handle}&showUnofficial={show_unofficial}')
