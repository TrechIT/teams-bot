import requests
from dotenv import dotenv_values
from typing import Any, Dict
import httpx
import asyncio
import utils

# Load config from .env
config = dotenv_values()

HALO_BASE_URL = config["HALO_BASE_URL"]
HALO_CLIENT_ID = config["HALO_CLIENT_ID"]
HALO_CLIENT_SECRET = config["HALO_CLIENT_SECRET"]


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


def get_kb_token():
    url = f"{HALO_BASE_URL}/auth/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": HALO_CLIENT_ID,
        "client_secret": HALO_CLIENT_SECRET,
        "scope": "read:kb",
    }

    try:
        with httpx.Client() as client:
            resp = client.post(
                url,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
            resp.raise_for_status()
            # print(resp.json()["access_token"])
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


def get_knowledge_base_article(article_id: int, token):
    # TODO: Implement this function to fetch knowledge base articles
    url = f"https://halo.trechit.com/api/KBArticle/{article_id}"
    try:
        with httpx.Client() as client:
            resp = client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        print("\n=== HTTP ERROR (KB) ===")
        print(f"URL: {e.request.url}")
        print(f"Status: {e.response.status_code}")
        print(f"Body: {e.response.text}")
        print("===========================\n")
        raise


def get_knowledge_base_contents(token):
    url = f"https://halo.trechit.com/api/KBArticle"
    try:
        with httpx.Client() as client:
            resp = client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            response = resp.json()
            return [a["id"] for a in response["articles"]]
    except httpx.HTTPStatusError as e:
        print("\n=== HTTP ERROR (KB) ===")
        print(f"URL: {e.request.url}")
        print(f"Status: {e.response.status_code}")
        print(f"Body: {e.response.text}")
        print("===========================\n")
        raise


async def main():
    # test_ticket_id = 2267
    # try:
    # ticket = await get_ticket(test_ticket_id)
    # print(ticket)
    token = get_kb_token()
    kb_contents = get_knowledge_base_contents(token)
    for article_id in kb_contents:
        response = get_knowledge_base_article(article_id, token)
        try:
            utils.export_article_to_txt(response)
        except Exception as e:
            print(f"Error exporting article: {e}")


# except Exception as e:
# print(f"Error in main(): {e}")


if __name__ == "__main__":
    asyncio.run(main())
