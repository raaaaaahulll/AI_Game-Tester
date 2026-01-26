"""
Custom exceptions for the AI Game Testing System.
"""
from typing import Optional


class GameTestingException(Exception):
    """Base exception for all game testing errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class TestingSessionError(GameTestingException):
    """Raised when there's an error with a testing session."""
    pass


class TestingSessionAlreadyRunningError(TestingSessionError):
    """Raised when trying to start a test while one is already running."""
    pass


class TestingSessionNotRunningError(TestingSessionError):
    """Raised when trying to stop a test that isn't running."""
    pass


class InvalidGenreError(GameTestingException):
    """Raised when an invalid game genre is provided."""
    pass


class EnvironmentError(GameTestingException):
    """Raised when there's an error initializing the game environment."""
    pass


class AgentError(GameTestingException):
    """Raised when there's an error with the RL agent."""
    pass


class MetricsError(GameTestingException):
    """Raised when there's an error accessing metrics."""
    pass

