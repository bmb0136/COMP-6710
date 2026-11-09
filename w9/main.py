import os
import subprocess
from pathlib import Path
from typing import cast
from allpairspy import AllPairs

INPUT_DIR = Path("./detr-main")
OUTPUT_DIR = Path("./output")
CONFIGURATIONS: list[list[list[str]]] = [
    [["-a", "file"], ["-a", "vuln"]],
    [[""], ["-l"], ["-ll"], ["-lll"]],
    [[""], ["-i"], ["-ii"], ["-iii"]],
    [["-f", "csv"], ["-f", "custom"], ["-f", "html"], ["-f", "json"], ["-f", "screen"], ["-f", "txt"], ["-f", "xml"], ["-f", "yaml"]]
]

def main():
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    for i, config in enumerate(AllPairs(CONFIGURATIONS)):  # pyright: ignore[reportUnknownVariableType]
        config = cast(list[list[str]], config)
        with open(OUTPUT_DIR / f"{i}.txt", "w") as f:
            _ = f.write(f"Config = {config}\n")

            cmd = ["bandit", "-r", str(INPUT_DIR)]
            for option in config:
                cmd.extend([x for x in option if x])
            _ = f.write(f"Command = {" ".join(cmd)}")
            print(f"Running: `{" ".join(cmd)}`")

            _ = f.write("\n\n==========\n\n")
            f.flush()

            try:
                p = subprocess.run(cmd, stdout=f, stderr=f)
                _ = f.write(f"Exit code = {p.returncode}\n")
            except Exception as e:
                _ = f.write(f"Failed to run bandit: {e}\n")

if __name__ == "__main__":
    main()
