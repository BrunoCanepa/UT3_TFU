from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from jose import jwt
from jose.exceptions import JWTError
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"
JWKS_URL = f"{AUTH0_ISSUER}.well-known/jwks.json"
BACKEND_URL = f"http://localhost:{os.getenv('BACKEND_PORT')}"
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT"))

app= FastAPI("Api Gateway")

jwks_client= None

async def get_jwks(): #agarro clave pubica de auth0
    global jwks_client
    if jwks_client is None:
        async with httpx.AsyncClient() as client:
            r = await client.get(JWKS_URL)
            jwks_client = r.json()
    return jwks_client

def get_signing_key(token_kid, jwks):
    for key in jwks["keys"]:
        if key["kid"] == token_kid:
            return key
    return None


#aca viene lo chido
async def verify_token(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token faltante")
    token = auth.split(" ")[1]

    jwks = await get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    key = get_signing_key(unverified_header["kid"], jwks)
    if not key:
        raise HTTPException(status_code=401, detail="No se encontró la clave")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER,
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

    # Guardamos datos de usuario en request.state para pasarlos al backend
    request.state.user = {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "name": payload.get("name")
    }
    print(f"Gateway: token válido para {payload.get('email') or payload.get('sub')}")
    return payload