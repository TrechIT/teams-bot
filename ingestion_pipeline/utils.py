import os
import sys

SECRETS_PATH = "/run/secrets"


def get_config_value(key: str) -> str:
    """
    Attempts to read a secret from a mounted file, falling back to a standard
    environment variable for local development.
    """
    secret_file_path = os.path.join(SECRETS_PATH, key.lower())
    try:
        with open(secret_file_path, "r") as f:
            # Secrets often have trailing newlines, so strip them
            return f.read().strip()
    except FileNotFoundError:
        print(
            f"Error: Configuration key '{key}' not found in Docker Secrets or environment variables.",
            file=sys.stderr,
        )
