from pathlib import Path

from examples._env import is_fast_mode
from examples.run import run_and_save

if __name__ == "__main__":
    run_and_save("gaussian_location", Path("docs/gallery"), quick=is_fast_mode())
