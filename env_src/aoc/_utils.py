import configparser
import requests
import html2text
from pathlib import Path
import datetime
import logging
from bs4 import BeautifulSoup
import json
import time
import subprocess

logger = logging.getLogger(__name__)

# --- CONFIGURATION & PATHS ---

# The root of the project is two levels up from this file (env_src/aoc/_utils.py)
PROJECT_ROOT = Path(__file__).parent.parent.parent
CACHE_DIR = PROJECT_ROOT / ".cache"
CONFIG_FILE_PATH = Path(__file__).parent.parent / "config.ini"
CONTEXT_FILE_PATH = PROJECT_ROOT / ".context.json"
PROGRESS_JSON_PATH = PROJECT_ROOT / "progress.json"
AOC_BASE_URL = "https://adventofcode.com"

def read_context() -> tuple[int, int] | None:
    """Reads the persisted year and day from the context file."""
    if not CONTEXT_FILE_PATH.exists():
        return None
    try:
        with open(CONTEXT_FILE_PATH, 'r') as f:
            data = json.load(f)
            if "year" in data and "day" in data:
                return data["year"], data["day"]
    except (json.JSONDecodeError, KeyError):
        logger.warning("Could not read .context.json, file may be corrupt.")
        return None
    return None

def write_context(year: int, day: int):
    """Saves the year and day to the context file."""
    with open(CONTEXT_FILE_PATH, 'w') as f:
        json.dump({"year": year, "day": day}, f, indent=2)

def clear_context():
    """Removes the context file."""
    if CONTEXT_FILE_PATH.exists():
        CONTEXT_FILE_PATH.unlink()


# --- HELPER FUNCTIONS ---

def _read_answers_cache(year: int, day: int) -> dict:
    """Reads the answers.json cache for a given day."""
    cache_file = CACHE_DIR / str(year) / f"{day:02d}" / "answers.json"
    if not cache_file.exists():
        # Return the default structure if the file doesn't exist
        return {
            "part_1": {"correct_answer": None, "submissions": []},
            "part_2": {"correct_answer": None, "submissions": []}
        }
    with open(cache_file, 'r') as f:
        return json.load(f)

def _write_answers_cache(year: int, day: int, data: dict):
    """Writes data to the answers.json cache for a given day."""
    cache_dir = CACHE_DIR / str(year) / f"{day:02d}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "answers.json"
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2)

def get_session_cookie() -> str | None:
    """Reads the session cookie from the config file."""
    if not CONFIG_FILE_PATH.exists():
        return None
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("user", "session_cookie", fallback=None)

def get_bool_config_setting(key: str, default: bool = False) -> bool:
    """Reads a boolean setting from the [user] section of the config file."""
    if not CONFIG_FILE_PATH.exists():
        return default
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.getboolean("user", key, fallback=default)

def get_aoc_data(year: int, day: int, data_type: str) -> str:
    """
    Fetches data from the website, with robust caching.
    data_type can be 'instructions' or 'input'.
    """
    # Determine the correct URL path ('input' or just the day page)
    url_path = f"/{year}/day/{day}/input" if data_type == "input" else f"/{year}/day/{day}"

    # Determine the cache filename
    file_extension = "md" if data_type == "instructions" else "txt"
    cache_file = CACHE_DIR / str(year) / f"{day:02d}" / f"{data_type}.{file_extension}"

    # 1. Check cache first
    if cache_file.exists():
        logger.info(f"Loaded {data_type} for {year}-{day} from cache.\n")
        return cache_file.read_text()

    # 2. If not in cache, fetch from web
    logger.info(f"Cache miss. Fetching {data_type} for {year}-{day} from web.\n")
    session_cookie = get_session_cookie()
    if not session_cookie:
        raise ConnectionError("Session cookie not found. Please run 'aoc setup'.")

    url = f"{AOC_BASE_URL}{url_path}"
    headers = {"User-Agent": "aoc-env by apsurt"}
    cookies = {"session": session_cookie}

    response = requests.get(url, headers=headers, cookies=cookies)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

    content = response.text

    if data_type == "instructions":
            content = format_instructions(content)

    # 3. Save to cache
    logger.info(f"Saving {data_type} for {year}-{day} to cache.\n")
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(content)

    # After fetching, check if we should also cache answers for solved puzzles
    try:
        if PROGRESS_JSON_PATH.exists():
            with open(PROGRESS_JSON_PATH, 'r') as f:
                progress_data = json.load(f).get("progress", {})

            stars = progress_data.get(str(year), {}).get(str(day), 0)

            if stars > 0:
                answers_cache = _read_answers_cache(year, day)
                part1_answered = answers_cache.get("part_1", {}).get("correct_answer") is not None
                part2_answered = answers_cache.get("part_2", {}).get("correct_answer") is not None

                # Only scrape if we are missing at least one answer
                if not (part1_answered and part2_answered):
                    logger.info(f"Fetching correct answers for solved puzzle {year}-{day}...")
                    correct_answers = scrape_day_page_for_answers(year, day)
                    if correct_answers:
                        for part, answer in correct_answers.items():
                            part_key = f"part_{part}"
                            if answers_cache.get(part_key, {}).get("correct_answer") is None:
                                answers_cache[part_key]["correct_answer"] = answer
                        _write_answers_cache(year, day, answers_cache)
    except Exception as e:
        logger.warning(f"Could not check for/cache correct answers during data fetch: {e}")


    return content

def format_instructions(html_content: str) -> str:
    """Converts puzzle instruction HTML to readable terminal text."""
    h = html2text.HTML2Text()
    h.body_width = 80  # Wrap text at 80 characters
    # Extract only the content of the <article> tags
    # This avoids printing the whole HTML page header/footer
    start = html_content.find('<article')
    end = html_content.rfind('</article>') + len('</article>')
    if start != -1 and end != -1:
        html_content = html_content[start:end]

    return h.handle(html_content)

def get_latest_puzzle_date() -> tuple[int, int]:
    """
    Gets the latest available puzzle year and day based on EST.
    AoC puzzles unlock at midnight EST (UTC-5).
    """
    # Current time in UTC
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # Convert to EST (UTC-5)
    est_offset = datetime.timedelta(hours=-5)
    now_est = now_utc + est_offset

    year = now_est.year
    day = now_est.day

    # If it's before December, use the last day of the previous year's calendar
    if now_est.month < 12:
        return year - 1, 25

    # During December, cap the day at 25
    if now_est.day > 25:
        return year, 25

    return year, day

def post_answer(year: int, day: int, part: int, answer) -> str:
    """
    Submits an answer, with full caching support.
    Checks cache before submitting and saves the result after.
    """
    part_key = f"part_{part}"
    str_answer = str(answer)

    # 1. Check cache before doing anything
    cached_data = _read_answers_cache(year, day)

    # Check if this exact answer has been submitted before
    for sub in cached_data[part_key]["submissions"]:
        if sub["answer"] == str_answer:
            logger.info(f"Answer '{str_answer}' found in cache. Returning cached result.")
            return sub["result"]

    # Check if we already know the correct answer
    if cached_data[part_key]["correct_answer"] is not None:
        logger.warning(f"Correct answer for Part {part} is already known. Submission cancelled.")
        return "You don't seem to be solving the right level. Did you already complete it?"

    # 2. If not in cache, proceed with web submission
    logger.info(f"Answer '{str_answer}' not in cache. Submitting to AoC website.")
    session_cookie = get_session_cookie()
    if not session_cookie:
        raise ConnectionError("Session cookie not found. Please run 'aoc setup'.")

    url = f"{AOC_BASE_URL}/{year}/day/{day}/answer"
    headers = {"User-Agent": "aoc-env by your-github-username (caching submissions)"}
    cookies = {"session": session_cookie}
    payload = {"level": part, "answer": str_answer}

    response = requests.post(url, headers=headers, cookies=cookies, data=payload)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    response_text = soup.find("article").p.get_text()

    # 3. Save the new result to the cache
    logger.info("Saving new submission result to cache.")
    cached_data[part_key]["submissions"].append({
        "answer": str_answer,
        "result": response_text
    })
    # If correct, also store it in the 'correct_answer' field
    if "That's the right answer!" in response_text:
        cached_data[part_key]["correct_answer"] = str_answer

    _write_answers_cache(year, day, cached_data)

    return response_text

def scrape_year_progress(year: int) -> dict[int, int]:
    """
    Scrapes the main page of a given year to get puzzle completion status.

    Returns:
        A dictionary mapping each day (int) to its star count (0, 1, or 2).
    """
    logger.info(f"Scraping progress for year {year}...")
    session_cookie = get_session_cookie()
    if not session_cookie:
        raise ConnectionError("Session cookie not found. Please run 'aoc setup'.")

    url = f"{AOC_BASE_URL}/{year}"
    headers = {"User-Agent": "aoc-env by your-github-username (scraping progress)"}
    cookies = {"session": session_cookie}

    response = requests.get(url, headers=headers, cookies=cookies)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    progress = {}

    calendar = soup.find("pre", class_="calendar")
    if not calendar:
        logger.warning(f"Could not find calendar element for year {year}.")
        return {}

    # Find all the day links within the calendar
    day_links = calendar.find_all("a")
    if not day_links:
        return {} # No participation this year

    for link in day_links:
        label = link.get("aria-label", "")
        day_span = link.find("span", class_="calendar-day")

        # Skip any links that aren't properly formed day entries
        if not label or not day_span:
            continue

        try:
            day = int(day_span.get_text().strip())

            if "two stars" in label:
                stars = 2
            elif "one star" in label:
                stars = 1
            else:
                stars = 0

            progress[day] = stars
        except (ValueError, TypeError):
            continue

    return progress

def scrape_day_page_for_answers(year: int, day: int) -> dict[int, str]:
    """
    Scrapes a puzzle day's page to find any revealed correct answers.

    Returns:
        A dictionary mapping the part number (1 or 2) to the correct answer (str).
    """
    logger.info(f"Checking for correct answers on page for {year}-{day}...")
    session_cookie = get_session_cookie()
    if not session_cookie:
        # Don't raise an error, just return empty if not configured
        return {}

    url = f"{AOC_BASE_URL}/{year}/day/{day}"
    headers = {"User-Agent": "aoc-env by your-github-username (scraping answers)"}
    cookies = {"session": session_cookie}

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
    except requests.RequestException:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    answers = {}

    # The answer is typically in a <p> tag right after the puzzle text.
    # The key phrase is "Your puzzle answer was <code>...</code>"
    for p_tag in soup.find_all("p"):
        if "Your puzzle answer was" in p_tag.get_text():
            answer_code = p_tag.find("code")
            if answer_code:
                # The first one found is Part 1, the second is Part 2
                part = 1 if 1 not in answers else 2
                answers[part] = answer_code.get_text()
                logger.info(f"Found correct answer for Part {part}: {answers[part]}")

    return answers

def _read_tests_cache(year: int, day: int) -> dict:
    """Reads the tests.json cache for a given day."""
    cache_file = CACHE_DIR / str(year) / f"{day:02d}" / "tests.json"
    if not cache_file.exists():
        return {"part_1": [], "part_2": []}
    with open(cache_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"part_1": [], "part_2": []} # Return default on file corruption

def _write_tests_cache(year: int, day: int, data: dict):
    """Writes test case data to the tests.json cache for a given day."""
    cache_dir = CACHE_DIR / str(year) / f"{day:02d}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "tests.json"
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2)

def git_commit_solution(year: int, day: int, part: int):
    """
    Stages and commits a solution file with a standardized message.
    """
    logger = logging.getLogger(__name__)
    solution_path = PROJECT_ROOT / "solutions" / str(year) / f"{day:02d}" / f"part_{part}.py"
    # Also good to commit the progress file if it has changed
    progress_path = PROJECT_ROOT / "progress.json"

    commit_message = f"feat({year}-{day:02d}): Solve Part {part}"

    try:
        # Check if we are in a git repository and there are changes to commit
        status_check = subprocess.run(
            ["git", "status", "--porcelain", str(solution_path)],
            capture_output=True, text=True, check=True
        )
        # If the output is empty, the file is not changed or not tracked
        if not status_check.stdout.strip():
            logger.info("No changes to solution file to commit.")
            return

        logger.info(f"Staging and committing solution with message: '{commit_message}'")

        # Stage the files
        subprocess.run(["git", "add", str(solution_path)], check=True)
        if progress_path.exists():
            subprocess.run(["git", "add", str(progress_path)], check=True)

        # Commit the changes
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        logger.info("Auto-commit successful.")

    except FileNotFoundError:
        logger.error("Auto-commit failed: 'git' command not found. Is Git installed and in your PATH?")
    except subprocess.CalledProcessError as e:
        logger.error(f"Auto-commit failed: A git command failed to execute.\nError: {e.stderr}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during auto-commit: {e}")
