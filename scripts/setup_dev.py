#!/usr/bin/env python3
"""Developer environment setup script.

Run once after cloning:
  python scripts/setup_dev.py
"""

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], **kwargs) -> None:  # type: ignore[no-untyped-def]
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.run(cmd, check=True, **kwargs)


def main() -> None:
    root = Path(__file__).parent.parent

    print("=== ARQYV Dev Setup ===")

    # Install dev deps
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])
    run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"])

    # Install spaCy model
    run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

    # Pre-commit hooks
    run(["pre-commit", "install"])

    # Create .env from template if missing
    env_file = root / ".env"
    env_example = root / ".env.example"
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print(f"Created {env_file} from template.")

    print("\n✓ Dev environment ready. Run: arqyv --debug")


if __name__ == "__main__":
    main()
