from .auth import router as auth
from .teams import router as teams
from .plays import router as plays

__all__ = ["auth", "teams", "plays"]
