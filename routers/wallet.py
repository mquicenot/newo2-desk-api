from fastapi import APIRouter, Security, HTTPException, Query
from fastapi.responses import JSONResponse
from auth0_manager.utils import VerifyToken  # Clase para la verificación de tokens de Auth0
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from routers import auth0
from neo4j_manager.utils.wallet import Neo4jWallet  # Clase para interactuar con Neo4j

# Se crea un router de FastAPI para definir los endpoints de esta sección
query = APIRouter()

# Instancia de la clase de autenticación
auth = VerifyToken()

# Instancia de la clase para realizar operaciones en Neo4j
post = Neo4jWallet()

class EliminarTarjeta(BaseModel):
    user_id:str=Field(...,description='Identificador del usuario')
    empresa_id:str=Field(...,description='Identificador de la empresa')
    tarjeta_id:str=Field(...,description='Identificador de la tarjeta')



@query.get("/obtener_wallet", tags=['Wallet'], summary="Obtener equipo en la base de datos")
def obtener_equipo(user_id: str = Query(..., title="Identificador del usuario"), 
                empresa_id: str = Query(..., title="Identificador de la empresa")):  # user_id: str = Query(..., title="Identificador del usuario"), empresa_id: str = Query(..., title="Identificador de la empresa"
    """
    Este endpoint permite modificar un equipo en la base de datos.

    Parámetros:
    - `user_id` (str): Identificador del usuario.
    - `empresa_id` (str): Identificador de la empresa.

    Respuesta:
    - `200`: Modificación exitosa.
    - `400`: Error en la operación.
    """
    try:
        # Convertir los parámetros en un diccionario
        records = [{
            'user_id': user_id,
            'empresa_id': empresa_id,
        }]
        # Ejecutar la operación en Neo4j
        response = post.ObtenerWallet(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@query.put("/eliminar_tarjeta", tags=['Wallet'], summary="Obtener equipo en la base de datos")
def obtener_equipo(payload:EliminarTarjeta):  # user_id: str = Query(..., title="Identificador del usuario"), empresa_id: str = Query(..., title="Identificador de la empresa"
    """
    Este endpoint permite modificar un equipo en la base de datos.

    Parámetros:
    - `user_id` (str): Identificador del usuario.
    - `empresa_id` (str): Identificador de la empresa.

    Respuesta:
    - `200`: Modificación exitosa.
    - `400`: Error en la operación.
    """
    try:
        # Convertir los parámetros en un diccionario
        records = [{
            **payload.model_dump()
        }]
        # Ejecutar la operación en Neo4j
        response = post.EliminarTarjeta(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))