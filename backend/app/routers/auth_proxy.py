from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def proxy_login(credentials: LoginRequest):
    """
    Proxy login request to maxplatform authentication server.
    This avoids CORS issues by making the request server-side.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Forward the login request to maxplatform
            response = await client.post(
                f"{settings.MAXPLATFORM_API_URL}/api/auth/login",
                json=credentials.model_dump(),
                timeout=httpx.Timeout(10.0)
            )
            
            # Return the response as-is
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Authentication failed")
                )
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Cannot connect to authentication server: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication error: {str(e)}"
            )