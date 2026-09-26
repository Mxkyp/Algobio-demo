from fastapi import status
from algobio.auth.model import NormalizedOAuth2Profile
from algobio.auth.callback import available_providers


class FakeProvider:
    def get_login_url(self) -> str:
        return "https://fake.login.url"

    async def get_profile(self, code: str) -> NormalizedOAuth2Profile:
        return NormalizedOAuth2Profile(
            email="testfake@test.com",
            provider="fake",
            external_id="fake-id-123",
            name="Fake User"
        )


def test_auth_callback_issues_jwt(client, test_engine):
    # Setup FakeProvider
    available_providers["fake"] = FakeProvider()
    
    # WHEN hitting the callback
    response = client.get("/auth/callback/fake?code=some_fake_code", follow_redirects=False)

    # Clean up
    available_providers.pop("fake", None)

    # THEN
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT, response.text
    assert "algobio_token" in response.cookies
