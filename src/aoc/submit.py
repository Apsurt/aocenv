from typing import Any
import requests
from .context import get_context
from .configuration import get_session_cookies, get_config, write_config
from .bind import run_bind
from .cache import read_submit_cache, write_submit_cache
from bs4 import BeautifulSoup


def handle_response(msg: str, response_type: str):
    # TODO Better printing
    print(msg)
    print(response_type)


def classify_response(msg: str) -> str:
    if "That's the right answer" in msg:
        return "CORRECT"
    if "That's not the right answer" in msg:
        return "WRONG"
    if "You gave an answer too recently" in msg:
        return "TOO_FAST"
    if "Did you already complete it" in msg:
        return "ANSWERED"
    if "You need to actually provide an answer before you hit the button" in msg:
        return "NO_ANSWER"
    raise RuntimeError(
        "CRITICAL -- Got invalid message from advent of code, please report this bug on: https://github.com/Apsurt/aocenv/issues"
    )


def submit(answer: Any):
    answer = str(answer)

    cookies = get_session_cookies()
    ctx = get_context()

    cache = read_submit_cache(ctx, cookies, answer)
    if cache:
        reponse_type = classify_response(cache)
        handle_response(cache, reponse_type)
        return

    payload = {"level": ctx.part, "answer": answer}

    cookies = get_session_cookies()
    if not cookies or "session" not in cookies:
        raise ValueError("Session cookie is not set.")

    url = f"https://adventofcode.com/{ctx.year}/day/{ctx.day}/answer"

    response = requests.post(url, data=payload, cookies=cookies, allow_redirects=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    article = soup.find("article")
    if article:
        msg = article.get_text().strip()
    else:
        raise RuntimeError(
            "Did not find what we were looking for. Are your session cookies up-to-date?"
        )

    assert isinstance(msg, str)

    # cases:
    # CORRECT CACHE
    # WRONG CACHE
    # TOO_FAST NOCACHE
    # ANSWERED NOCACHE
    # NO_ANSWER NOCACHE
    reponse_type = classify_response(msg)
    if reponse_type in ["TOO_FAST", "ANSWERED", "NO_ANSWER"]:
        pass
    if reponse_type in ["WRONG", "CORRECT"]:
        write_submit_cache(ctx, cookies, answer, msg)

    handle_response(msg, reponse_type)

    if reponse_type == "CORRECT":
        config = get_config()

        if config.getboolean("settings", "auto_bump_on_correct"):
            current_year = ctx.year
            current_day = ctx.day
            current_part = ctx.part

            new_year = current_year
            new_day = current_day
            new_part = current_part

            if current_part == 1:
                new_part = 2
            elif current_part == 2:
                if current_day == 25:
                    new_day = 1
                    new_part = 1
                    new_year = current_year + 1
                else:
                    new_day = current_day + 1
                    new_part = 1

            # Update config
            config.set("variables", "default_year", str(new_year))
            config.set("variables", "default_day", str(new_day))
            config.set("variables", "default_part", str(new_part))
            write_config(config)

        if config.getboolean("settings", "bind_on_correct"):
            print("Correct answer! Binding solution...")
            run_bind(name=None, force=False)
