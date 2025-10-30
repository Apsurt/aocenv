import requests
from .context import get_context
from .configuration import get_session_cookies
from bs4 import BeautifulSoup

def handle_response(msg: str):
    # cases:
    # wrong CACHE
    # correct CACHE
    # too fast NOCACHE
    # already answered NOCACHE
    pass

def submit(answer: str):
    #TODO add cache

    ctx = get_context()

    print(ctx)

    payload = {
        "level": ctx.part,
        "answer": answer
    }

    cookies = get_session_cookies()
    if not cookies or "session" not in cookies:
        raise ValueError("Session cookie is not set.")

    url = f"https://adventofcode.com/{ctx.year}/day/{ctx.day}/answer"

    response = requests.post(url, data=payload, cookies=cookies, allow_redirects=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    msg = soup.find("article").get_text().strip()
    handle_response(msg)
