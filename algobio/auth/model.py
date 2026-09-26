from typing import Protocol
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel


class NormalizedOAuth2Profile(BaseModel):
    email: str
    provider: str
    external_id: str
    name: str


class AuthPrincipal:
    def __init__(self, user):
        self.user = user


class OAuth2Provider(Protocol):
    def get_login_url(self) -> str: ...

    async def get_profile(self, code: str) -> NormalizedOAuth2Profile: ...


class GoogleProvider:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"

    def get_login_url(self) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }

        return f"{self.auth_url}?{urlencode(params)}"

    async def get_profile(self, code: str) -> NormalizedOAuth2Profile:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()

            token_data = token_response.json()
            access_token = token_data["access_token"]

            profile_response = await client.get(
                self.userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()

        return NormalizedOAuth2Profile(
            email=profile_data["email"],
            provider="google",
            external_id=profile_data["sub"],
            name=profile_data.get("name", ""),
        )
