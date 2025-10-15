from dataclasses import dataclass

@dataclass
class Context:
    year: int
    day: int
    part: int

def get_context():
    return Context(2024, 1, 1)
