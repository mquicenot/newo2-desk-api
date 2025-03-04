from fastapi import APIRouter, Security, HTTPException, Query
from fastapi.responses import JSONResponse
from auth0_manager.utils import VerifyToken  # Clase para la verificación de tokens de Auth0
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from routers import auth0
from neo4j_manager.utils.compras import Neo4jCompras  # Clase para interactuar con Neo4j

# Se crea un router de FastAPI para definir los endpoints de esta sección
query = APIRouter()

# Instancia de la clase de autenticación
auth = VerifyToken()

# Instancia de la clase para realizar operaciones en Neo4j
post = Neo4jCompras()


class CompraIlimitadoIndividual(BaseModel):

    """
    Modelo para modificar un equipo en la base de datos.
    """
    user_id: str = Field(..., description="ID único del usuario que realiza la acción.")
    empresa_id: str = Field(..., description="ID de la empresa a la que pertenece el usuario.")
    integrante_id: str = Field(..., description="ID del integrante dentro de la empresa, si aplica.")


@query.post("/crear_equipo", tags=['Compras'], summary="Modificar equipo en la base de datos")
def modificar_equipo(payload: CompraIlimitadoIndividual):
    """
    Este endpoint permite modificar un equipo en la base de datos.

    Parámetros:
    - `auth_id` (str): Identificador del usuario.
    - `empresa_id` (str): Identificador de la empresa.
    - `nombre_equipo` (str): Nuevo nombre del equipo.
    - `descripcion` (str): Nueva descripción del equipo.
    - `pago_invitados` (bool): Indica si hay pago por invitados.
    - `pago_reservas` (bool): Indica si hay pago por reservas.

    Respuesta:
    - `200`: Modificación exitosa.
    - `400`: Error en la operación.
    """
    try:
        # Convertir el payload a diccionario
        records = [payload.dict()]
        
        print(records)
        
        # Ejecutar la operación en Neo4j
        response = post.IlimitadoIndividual(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

