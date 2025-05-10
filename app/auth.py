from fastapi import Depends, HTTPException, Request, status

def get_token_from_header(request: Request) -> str:
    """Extract and validate the token from the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    # Extract the token
    token = auth_header.split(" ")[1]
    return token
