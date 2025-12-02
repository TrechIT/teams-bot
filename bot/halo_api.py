import httpx
import asyncio
import os
import sys

SECRETS_PATH = "/run/secrets"


def get_config_value(key: str) -> str:
    """
    Attempts to read a secret from a mounted file
    """
    secret_file_path = os.path.join(SECRETS_PATH, key.lower())
    try:
        with open(secret_file_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(
            f"Error: Configuration key '{key}' not found in Docker Secrets.",
            file=sys.stderr,
        )


HALO_BASE_URL = get_config_value("HALO_BASE_URL")
HALO_CLIENT_ID = get_config_value("HALO_CLIENT_ID")
HALO_CLIENT_SECRET = get_config_value("HALO_CLIENT_SECRET")


async def get_ticket_token():
    url = f"{HALO_BASE_URL}/auth/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": HALO_CLIENT_ID,
        "client_secret": HALO_CLIENT_SECRET,
        "scope": "read:tickets",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
            resp.raise_for_status()
            # print(resp.json()["access_token"])
            resp.raise_for_status()
            token_data = resp.json()
            return token_data["access_token"]
    except httpx.HTTPStatusError as e:
        print("\n=== HTTP ERROR (TOKEN) ===")
        print(f"URL: {e.request.url}")
        print(f"Status: {e.response.status_code}")
        print(f"Body: {e.response.text}")
        print("=========================\n")
        raise


async def get_ticket(ticket_id: int):
    token = await get_ticket_token()
    # print(token)
    url = f"{HALO_BASE_URL}/api/tickets/{ticket_id}"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        print("\n=== HTTP ERROR (TICKET) ===")
        print(f"URL: {e.request.url}")
        print(f"Status: {e.response.status_code}")
        print(f"Body: {e.response.text}")
        print("===========================\n")
        raise
