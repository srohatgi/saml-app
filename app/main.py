from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from .auth import get_token_from_header
import httpx

# Load configuration
settings = Settings() 

app = FastAPI(title="SAML App")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
templates = Jinja2Templates(directory=settings.static_dir)

# Auth routes
@app.get("/login")
async def login():
    """Redirect to Auth0 login page"""
    return RedirectResponse(
        f"https://{settings.auth0_domain}/authorize"
        f"?response_type=code"
        f"&client_id={settings.auth0_client_id}"
        f"&redirect_uri={settings.auth0_callback_url}"
        f"&scope=openid profile email"
    )

@app.get("/callback")
async def callback(code: str):
    """Handle the Auth0 callback"""
    # Exchange the code for a token
    token_url = f"https://{settings.auth0_domain}/oauth/token"
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": settings.auth0_client_id,
        "client_secret": settings.auth0_client_secret,
        "code": code,
        "redirect_uri": settings.auth0_callback_url
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, json=token_payload)
        token_data = token_response.json()
    
    if "error" in token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Auth0 error: {token_data['error_description']}"
        )
    
    # Redirect to frontend with the access token as a hash parameter
    access_token = token_data.get("access_token")
    id_token = token_data.get("id_token")
    
    # Redirect back to the frontend with tokens
    return RedirectResponse(f"/#access_token={access_token}&id_token={id_token}")

@app.get("/api/user-info")
async def get_user_info(token: str = Depends(get_token_from_header)):
    """Get user information from Auth0"""
    user_info_url = f"https://{settings.auth0_domain}/userinfo"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            user_info_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or token expired"
            )
        
        return response.json()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "auth0_client_id": settings.auth0_client_id, 
            "auth0_domain": settings.auth0_domain
        }
    )

@app.get("/logout")
async def logout():
    """Log out the user"""
    return_to_url = "http://localhost:8000"  # Replace with your domain in production
    return RedirectResponse(
        f"https://{settings.auth0_domain}/v2/logout"
        f"?client_id={settings.auth0_client_id}"
        f"&returnTo={return_to_url}"
    )

@app.get("/api/protected", status_code=200)
async def protected_route(token: str = Depends(get_token_from_header)):
    """A sample protected API route"""
    return {"message": "You have accessed a protected route!"}
