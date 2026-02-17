from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


# =========================================================
# Base User Model
# =========================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None


# =========================================================
# User Registration
# =========================================================

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str

    password: str = Field(..., min_length=8)
    confirm_password: str

    @validator("password")
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


# =========================================================
# Login
# =========================================================

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# =========================================================
# User Response
# =========================================================

class UserResponse(UserBase):
    id: int
    is_verified: bool
    is_active: bool
    is_superuser: bool
    is_blocked: bool          # ← add this
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# =========================================================
# Tokens
# =========================================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenWithRefresh(Token):
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# =========================================================
# OTP Flows
# =========================================================

class VerifySignupOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)

    @validator("new_password")
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v


class VerifyEmailChangeOTPRequest(BaseModel):
    otp: str = Field(..., min_length=6, max_length=6)


# =========================================================
# Profile Updates
# =========================================================

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)


class UpdateEmailRequest(BaseModel):
    new_email: EmailStr
    current_password: str


class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @validator("new_password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v
