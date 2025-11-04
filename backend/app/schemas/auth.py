from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Schema para /login endpoint.
    """

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """
    Schema para /refresh endpoint.
    """

    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
