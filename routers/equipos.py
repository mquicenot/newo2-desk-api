from fastapi import APIRouter, Security, HTTPException
from fastapi.responses import JSONResponse
from auth0_manager.utils import VerifyToken  # Clase para la verificación de tokens de Auth0
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from routers import auth0
from neo4j_manager.utils.equipos import Neo4jEquipos  # Clase para interactuar con Neo4j

# Se crea un router de FastAPI para definir los endpoints de esta sección
query = APIRouter()

# Instancia de la clase de autenticación
auth = VerifyToken()

# Instancia de la clase para realizar operaciones en Neo4j
post = Neo4jEquipos()

class ModificarEquipo(BaseModel):
    """
    Modelo para modificar un equipo en la base de datos.
    """
    auth_id: str = Field(..., title="Identificador del usuario")
    equipo_id: str = Field(..., title="Identificador del equipo")
    nombre_equipo: Optional[str] = Field(None, title="Nombre del equipo")
    descripcion: Optional[str] = Field(None, title="Descripción del equipo")
    pago_invitados: Optional[bool] = Field(None, title="Pago por invitados")
    pago_reservas: Optional[bool] = Field(None, title="Pago por reservas")
    acceso_ilimitado: Optional[bool] = Field(None, title="Acceso Ilimitado")
    
# 📌 Endpoint para modificar equipo en la base de datos
@query.put("/actualizar_equipo", tags=['Equipos'], summary="Modificar equipo en la base de datos")
def modificar_equipo(payload: ModificarEquipo):
    """
    Este endpoint permite modificar un equipo en la base de datos.

    Parámetros:
    - `auth_id` (str): Identificador del usuario.
    - `equipo_id` (str): Identificador del equipo.
    - `nombre_equipo` (str): Nuevo nombre del equipo.
    - `descripcion` (str): Nueva descripción del equipo.
    - `pago_invitados` (bool): Indica si hay pago por invitados.
    - `pago_reservas` (bool): Indica si hay pago por reservas.

    Seguridad:
    - Se requiere autenticación con Auth0.

    Respuesta:
    - `200`: Modificación exitosa.
    - `400`: Error en la operación.
    """
    try:
        # Convertir el payload a diccionario
        records = [payload.dict()]

        print("Datos recibidos:", records)  # Debugging

        # Ejecutar la operación en Neo4j
        response = post.ModificarEquipos(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
