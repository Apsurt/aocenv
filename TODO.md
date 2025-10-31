# TODO

## `src/aoc/run.py`
- [ ] **Add timing of execution:** Implement a way to measure and display the execution time of the user's solution in `run_main`.

## `src/aoc/cache.py`
- [ ] **Implement `read_submit_cache`:** Complete the `read_submit_cache` function to read submission results from the cache.
- [ ] **Implement `write_submit_cache`:** Complete the `write_submit_cache` function to write submission results to the cache.

## `src/aoc/load.py`
- [ ] **Implement solution loading:** Implement the functionality to load a saved solution into `main.py`. This is currently a placeholder file.

## `src/aoc/submit.py`
- [ ] **Implement response handling:** In `handle_response`, parse the response message from Advent of Code to determine if the answer was correct, incorrect, submitted too recently, or already answered.
- [ ] **Add caching for submissions:** In `submit`, before sending a request, check if the answer has been submitted before by using the submission cache.

## `src/aoc/cli.py`
- [ ] **Add timing flag to `run` command:** Add a `--time` or similar flag to the `run` command to enable/disable the execution timing feature.
- [ ] **Implement `load` command:** Implement the `load` command to load a saved solution into `main.py`.
- [ ] **Implement `test` command:** Implement the `test` command. The purpose is "TBA" and is slated for v0.2.0.

## Refactor
- [ ] Refactor everything for v0.2.0

## Tests
- [ ] Add full test coverage for v0.2.0
