from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from auth0_manager.utils import VerifyToken  # 👈 Clase para la verificación de tokens de Auth0
from pydantic import BaseModel
from routers import auth0
from neo4j_manager.utils.init_component import Neo4jInitComopnents  # 👈 Clase para interactuar con Neo4j
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# Se crea un router de FastAPI para definir los endpoints de esta sección
query = APIRouter()

# Instancia de la clase de autenticación
auth = VerifyToken()
    
# Instancia de la clase para realizar operaciones en Neo4j
post = Neo4jInitComopnents()

# 📌 Endpoint para registrar cashback ganado
@query.get("/variables", tags=['init_component'], summary="Registrar cashback ganado")
def gain_cashback(user_id:str):
    """
    Este endpoint permite registrar cashback ganado por un cliente.

    Parámetros:
    - customer_id (str): Identificador del cliente.
    - value (float): Valor del cashback ganado.
    - porcentage (float): Porcentaje aplicado.
    - days (float): Días de validez del cashback.
    - detail (str, opcional): Descripción adicional.

    Seguridad:
    - Se requiere autenticación con Auth0.

    Respuesta:
    - 200: Registro exitoso.
    - 400: Error en la operación.
    """
    
    try:
        # Se construye el registro a insertar en la base de datos
        records = [{
            'auth_id': user_id
        }]
        
        # Se ejecuta la operación en Neo4j
        response = post.InitComponents(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})