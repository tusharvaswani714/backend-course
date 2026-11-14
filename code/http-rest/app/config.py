from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    jwt_secret: str = Field(default="", min_length=16, validate_default=True)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=60, gt=0)
    cookie_secure: bool = False
    verification_code_minutes: int = Field(default=10, gt=0)
    resend_limit: int = Field(default=3, gt=0)
    resend_window_minutes: int = Field(default=10, gt=0)


settings = Settings()
