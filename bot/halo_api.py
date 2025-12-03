import httpx
from config import DefaultConfig

CONFIG = DefaultConfig()


async def get_ticket_token():
    url = f"{CONFIG.HALO_BASE_URL}/auth/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": CONFIG.HALO_CLIENT_ID,
        "client_secret": CONFIG.HALO_CLIENT_SECRET,
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
    url = f"{CONFIG.HALO_BASE_URL}/api/tickets/{ticket_id}"

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
