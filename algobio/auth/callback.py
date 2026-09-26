from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from algobio.auth.model import AuthPrincipal, GoogleProvider, OAuth2Provider
from algobio.auth.services import AuthService
from algobio.dependencies import get_auth_service, get_config
from algobio.model.domain import User

router = APIRouter(
    prefix="/auth",
    tags=["webhooks", "authentication", "external"],
)
config = get_config()

available_providers: dict[str, OAuth2Provider] = {
    "google": GoogleProvider(
        config.google_client_id, config.google_client_secret, config.google_redirect_uri
    )
}


@router.get("/login/{provider_name}")
def login(provider_name: str):
    provider = available_providers.get(provider_name)

    if provider is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "provider_not_available")

    return RedirectResponse(provider.get_login_url())


@router.get("/callback/{provider_name}")
async def callback(
    provider_name: str, code: str, auth_service: AuthService = Depends(get_auth_service)
):
    provider = available_providers.get(provider_name)

    if provider is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "provider_not_available")

    profile = await provider.get_profile(code)

    user = auth_service.get_user_by_email(profile.email)

    if user is None:
        user = auth_service.create_user(profile)

    algobio_token = auth_service.create_jwt(user)

    response = RedirectResponse(url=config.frontend_url)
    response.set_cookie(
        key="algobio_token",
        value=algobio_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600 * 24 * 7,
    )

    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url=config.frontend_url)
    response.delete_cookie(
        key="algobio_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response
