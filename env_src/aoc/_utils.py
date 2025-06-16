import configparser
import requests
import html2text
from pathlib import Path
import datetime
import logging

logger = logging.getLogger(__name__)

# --- CONFIGURATION & PATHS ---

# The root of the project is two levels up from this file (env_src/aoc/_utils.py)
PROJECT_ROOT = Path(__file__).parent.parent.parent
CACHE_DIR = PROJECT_ROOT / ".cache"
CONFIG_FILE_PATH = Path(__file__).parent.parent / "config.ini"
AOC_BASE_URL = "https://adventofcode.com"

# --- HELPER FUNCTIONS ---

def get_session_cookie() -> str | None:
    """Reads the session cookie from the config file."""
    if not CONFIG_FILE_PATH.exists():
        return None
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("user", "session_cookie", fallback=None)

def get_aoc_data(year: int, day: int, data_type: str) -> str:
    """
    Fetches data from the website, with robust caching.
    data_type can be 'instructions' or 'input'.
    """
    # Determine the correct URL path ('input' or just the day page)
    url_path = f"/{year}/day/{day}/input" if data_type == "input" else f"/{year}/day/{day}"

    # Determine the cache filename
    file_extension = "md" if data_type == "instructions" else "txt"
    cache_file = CACHE_DIR / str(year) / str(day) / f"{data_type}.{file_extension}"

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
