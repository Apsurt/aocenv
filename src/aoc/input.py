import requests
from aoc.context import get_context
from aoc.configuration import get_session_cookies

def _get_input(context):
    url = f"https://adventofcode.com/{context.year}/day/{context.day}/input"
    cookies = get_session_cookies()
    response = requests.get(url, cookies=cookies)
    return response

def input():
    # TODO Add caching
    return str(_get_input(get_context()).content)
