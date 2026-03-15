from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql://pricing:pricing@localhost:5432/pricing"
    # Public-facing issuer URL (as it appears in JWT tokens)
    oidc_issuer: str = "http://localhost:8080/realms/pricing"
    # Internal JWKS URL (can differ in Docker deployments)
    oidc_jwks_url: str = ""
    oidc_audience: str = "pricing-app"
    cors_origins: List[str] = ["http://localhost:3000"]

    def model_post_init(self, __context) -> None:
        if not self.oidc_jwks_url:
            object.__setattr__(
                self,
                "oidc_jwks_url",
                f"{self.oidc_issuer}/protocol/openid-connect/certs",
            )

    class Config:
        env_file = ".env"


settings = Settings()
