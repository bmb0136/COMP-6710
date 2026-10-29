from dataclasses import dataclass
import random
import json
from typing import cast

@dataclass
class FuzzData:
    v1: object
    v2: object
    result: object | None
    error: Exception | None

def divide(v1 : object, v2 : object) -> object:
    return v1 / v2   # pyright: ignore[reportOperatorIssue, reportUnknownVariableType]

def _gen_value(naughty: list[str]) -> object:
    match random.randint(1, 3):
        case 1:
            return random.randint(-42, 42)
        case 2:
            return random.choice(naughty)
        case _:
            return None

def simpleFuzzer(naughty: list[str]) -> list[FuzzData]: 
    data: list[FuzzData] = []
    for _ in range(6767):
        v1 = _gen_value(naughty)
        v2 = _gen_value(naughty)
        result: object | None = None
        error: Exception | None = None
        try:
            result = divide(v1, v2)
        except Exception as e:
            error = e
        data.append(FuzzData(v1, v2, result, error))
    return data

if __name__=='__main__':
    with open("blns.json", "r") as f:
        naughty = [x for x in cast(list[str], json.load(f)) if x.isalnum()]

    data = [
        {
            "v1": x.v1,
            "v2": x.v2,
            "result": x.result,
            "error": str(x.error) if x.error else None
        }
        for x in simpleFuzzer(naughty)
    ]
    with open("crashes.json", "w") as f:
        json.dump([x for x in data if x["error"] is not None], f, indent=True)
    with open("successes.json", "w") as f:
        json.dump([x for x in data if x["error"] is None], f, indent=True)
