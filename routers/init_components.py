from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from auth0_manager.utils import VerifyToken  # 👈 Clase para la verificación de tokens de Auth0
from pydantic import BaseModel
from routers import auth0
from neo4j_manager.utils.init_component import Neo4jInitComopnents  # 👈 Clase para interactuar con Neo4j
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class createJhiUserWithMiembro(BaseModel):
    user_id: str = Field(..., title="Identificador del usuario")
    email: str = Field(..., title="Correo del usuario")

# Se crea un router de FastAPI para definir los endpoints de esta sección
query = APIRouter()

# Instancia de la clase de autenticación
auth = VerifyToken()
    
# Instancia de la clase para realizar operaciones en Neo4j
post = Neo4jInitComopnents()

# 📌 Endpoint para registrar cashback ganado
@query.get("/variables", tags=['init_component'], summary="Buscar variables para el inicio de sesión")
def variables(user_id:str, email: str):
    """
    Este endpoint permite registrar cashback ganado por un cliente.

    Parámetros:
    - user_id (str): Identificador del usuario auth0.
    - email (str): Correo del usuario auth0.

    Respuesta:
    - 200: Registro exitoso.
    - 400: Error en la operación.
    """
    
    try:
        # Se construye el registro a insertar en la base de datos
        records = [{
            'auth_id': user_id,
            'email':email
        }]
        
        # Se ejecuta la operación en Neo4j
        response = post.InitComponents(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
    
@query.post("/create_user", tags=['init_component'], summary="Registrar jhi user y unirlo al perfil")
def gain_cashback(payload: createJhiUserWithMiembro):
    """
    Este endpoint permite registrar cashback ganado por un cliente.

    Parámetros:
    - user_id (str): Identificador del usuario auth0.
    - email (str): Correo del usuario auth0.

    Respuesta:
    - 200: Registro exitoso.
    - 400: Error en la operación.
    """
    
    try:
        # Se construye el registro a insertar en la base de datos
        records = [{
            **payload.dict()
        }]

        print(records)
        
        # Se ejecuta la operación en Neo4j
        response = post.createJhiUserWithMiembro(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})