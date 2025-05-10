import os
from pydantic_settings import BaseSettings

DOTENV = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    """Application settings."""
    
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_callback_url: str
    static_dir : str = os.path.join(os.path.dirname(__file__), "static")
    
    class Config:
        env_file = DOTENV
        env_file_encoding = "utf-8"
