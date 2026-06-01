import os

from discord import utils
from aiohttp import BasicAuth, ClientSession


class OAuthClient:
    TOKEN_URL = "https://discord.com/api/oauth2/token"
    TOKEN_REVOKE_URL = "https://discord.com/api/oauth2/token/revoke"
    DEFAULT_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: list[str] | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes

    def get_auth_url(self, state: str) -> str:
        return utils.oauth_url(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scopes=self.scopes,
            state=state,
        )

    async def exchange_code(self, code: str) -> dict:
        async with ClientSession() as session:
            async with session.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers=self.DEFAULT_HEADERS,
                auth=BasicAuth(self.client_id, self.client_secret),
            ) as response:
                if response.ok:
                    return await response.json()
                else:
                    raise Exception("Could not exchange code.")

    async def refresh_token(self, refresh_token: str) -> dict:
        async with ClientSession() as session:
            async with session.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                headers=self.DEFAULT_HEADERS,
                auth=BasicAuth(self.client_id, self.client_secret),
            ) as response:
                if response.ok:
                    return await response.json()
                else:
                    raise Exception("Could not refresh token.")

    async def revoke_token(self, token: str) -> dict:
        async with ClientSession() as session:
            async with session.post(
                self.TOKEN_URL,
                data={
                    "token": token,
                },
                headers=self.DEFAULT_HEADERS,
                auth=BasicAuth(self.client_id, self.client_secret),
            ) as response:
                if response.ok:
                    return await response.json()
                else:
                    raise Exception("Could not revoke token.")


client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
redirect_uri = "https://excla.xyz/login/confirm"  # Move this to config file
scopes = ["identify", "guilds", "guilds.members.read"]  # Move this to config file

client = OAuthClient(client_id, client_secret, redirect_uri, scopes)
