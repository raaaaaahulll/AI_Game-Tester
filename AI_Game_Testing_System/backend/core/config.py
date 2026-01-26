"""
Configuration management for the AI Game Testing System.

Uses pydantic-settings for environment-based configuration with validation.
Supports .env files and environment variables.
"""
import os
from pathlib import Path
from typing import Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Base Directory
    BASE_DIR: Path = Path(__file__).parent.parent
    
    # Paths
    MODELS_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "models")
    LOGS_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "logs")
    
    @property
    def METRICS_FILE(self) -> Path:
        """Path to metrics JSON file."""
        return self.LOGS_DIR / "metrics.json"
    
    # Screen Capture Settings
    SCREEN_TOP: int = Field(default=0, description="Top coordinate for screen capture")
    SCREEN_LEFT: int = Field(default=0, description="Left coordinate for screen capture")
    SCREEN_WIDTH: int = Field(default=1920, description="Screen capture width")
    SCREEN_HEIGHT: int = Field(default=1080, description="Screen capture height")
    SCREEN_MONITOR: int = Field(default=1, description="Monitor number (1 for primary)")
    
    @property
    def SCREEN_SETTINGS(self) -> Dict[str, Any]:
        """Screen capture settings dictionary."""
        return {
            "top": self.SCREEN_TOP,
            "left": self.SCREEN_LEFT,
            "width": self.SCREEN_WIDTH,
            "height": self.SCREEN_HEIGHT,
            "monitor": self.SCREEN_MONITOR
        }
    
    # Preprocessing
    IMG_WIDTH: int = Field(default=84, ge=1, description="Preprocessed image width")
    IMG_HEIGHT: int = Field(default=84, ge=1, description="Preprocessed image height")
    FRAME_STACK_SIZE: int = Field(default=4, ge=1, description="Number of frames to stack")
    
    # RL Hyperparameters
    TIMESTEPS: int = Field(default=100000, ge=1, description="Total training timesteps")
    SAVE_INTERVAL: int = Field(default=10000, ge=1, description="Model save interval")
    
    # Server Settings
    API_HOST: str = Field(default="0.0.0.0", description="API server host")
    API_PORT: int = Field(default=8000, ge=1, le=65535, description="API server port")
    API_RELOAD: bool = Field(default=False, description="Enable auto-reload (dev only)")
    
    # CORS Settings
    CORS_ORIGINS: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins, or '*' for all"
    )
    
    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format: 'json' for structured, 'text' for human-readable"
    )
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of {valid_envs}")
        return v.lower()
    
    @property
    def IS_PRODUCTION(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"
    
    @property
    def IS_DEVELOPMENT(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()

# Backward compatibility exports (deprecated, use settings object)
BASE_DIR = settings.BASE_DIR
MODELS_DIR = settings.MODELS_DIR
LOGS_DIR = settings.LOGS_DIR
METRICS_FILE = settings.METRICS_FILE
SCREEN_SETTINGS = settings.SCREEN_SETTINGS
IMG_WIDTH = settings.IMG_WIDTH
IMG_HEIGHT = settings.IMG_HEIGHT
FRAME_STACK_SIZE = settings.FRAME_STACK_SIZE
TIMESTEPS = settings.TIMESTEPS
SAVE_INTERVAL = settings.SAVE_INTERVAL
API_HOST = settings.API_HOST
API_PORT = settings.API_PORT
