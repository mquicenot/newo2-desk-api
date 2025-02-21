from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from auth0_manager.requests import auth0Services
import os

load_dotenv()

query = APIRouter()
auth = auth0Services()

class TokenRequest(BaseModel):
    username: str
    password: str

class ForgetPassword(BaseModel):
    username: str

@query.post("/obtener_token", tags=['Auth'], summary="Obtener un token de acceso")
async def get_token(payload: TokenRequest):
    """
    Endpoint para obtener un token de acceso de Auth0 usando el nombre de usuario y la contraseña.
    
    Parámetros:
    - username (str): El nombre de usuario para autenticar.
    - password (str): La contraseña asociada al usuario.
    
    Respuesta:
    - 200: Si la autenticación es exitosa, devuelve un token de acceso.
    - 400: Si ocurre un error durante la autenticación.
    """
    try:
        # Llamamos al servicio para obtener el token de acceso
        response = auth.get_access_token(payload.username, payload.password)
        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        # Si ocurre un error, retornamos un error 400
        return JSONResponse(status_code=400, content={"detail": str(e)})

@query.post("/crear_usuario", tags=['Auth'], summary="Crear un nuevo usuario en Auth0")
async def create_user(payload: TokenRequest):
    """
    Endpoint para crear un nuevo usuario en Auth0.
    
    Parámetros:
    - username (str): El nombre de usuario para el nuevo usuario.
    - password (str): La contraseña del nuevo usuario.
    
    Respuesta:
    - 200: Si el usuario es creado exitosamente, devuelve un mensaje de éxito.
    - 400: Si ocurre un error durante la creación del usuario.
    """
    try:
        # Llamamos al servicio para crear un nuevo usuario
        response = auth.create_new_user(payload.username, payload.password)
        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        # Si ocurre un error, retornamos un error 400
        return JSONResponse(status_code=400, content={"detail": str(e)})