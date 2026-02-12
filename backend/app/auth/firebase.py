"""Firebase Admin SDK initialization and token verification."""
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings

_app = None
_bearer_scheme = HTTPBearer()


def init_firebase():
    """Initialize Firebase Admin SDK."""
    global _app
    if _app:
        return
    settings = get_settings()
    if settings.firebase_credentials_path:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        _app = firebase_admin.initialize_app(cred)
    elif settings.firebase_project_id:
        _app = firebase_admin.initialize_app(options={
            "projectId": settings.firebase_project_id,
        })
    else:
        # Will use GOOGLE_APPLICATION_CREDENTIALS env var
        _app = firebase_admin.initialize_app()


def verify_firebase_token(token: str) -> dict:
    """Verify a Firebase ID token and return the decoded claims."""
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )


async def get_firebase_user(
    cred: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    """FastAPI dependency that verifies the Bearer token and returns Firebase claims."""
    return verify_firebase_token(cred.credentials)
