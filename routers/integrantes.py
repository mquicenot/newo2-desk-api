from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, Field
from neo4j_manager.utils.integrantes import Neo4jIntegrantes  # Clase para interactuar con Neo4j

# Se crea un router de FastAPI para definir los endpoints de esta sección
query = APIRouter()

# Instancia de la clase para realizar operaciones en Neo4j
post = Neo4jIntegrantes()

class EditarIntegrante(BaseModel):
    user_id: str = Field(..., description='ID del usuario en Auth0')
    empresa_id: str = Field(..., description='ID de la empresa')
    integrante_id: str = Field(..., description='ID del integrante del equipo')
    equipo_id: str = Field(..., description='ID del equipo al que voy a transferir')
    bloqueo: bool = Field (..., description='Estado del usuario dentro de la empresa')

@query.get("/obtener_integrantes", tags=['Integrantes'], summary="Obtener equipo en la base de datos")
def obtener_integrantes(
    user_id: str = Query(..., title="Identificador del usuario"),
    empresa_id: str = Query(..., title="Identificador de la empresa"),
    bloqueo: Optional[bool] = Query(None, title="Integrantes bloqueados"),
    equipo_id: Optional[str] = Query(None, title="Equipo del que queremos obtener los integrantes"),
    integrantes: Optional[str] = Query(None, title="Identificación, login o nombre para filtrar los usuarios"),
    tamanio_pagina: int = Query(10, title="Cantidad de registros por página", ge=1),
    pagina: int = Query(0, title="Número de página a consultar (inicia en cero)", ge=0)):
    """
    Este endpoint permite consultar los integrantes de un equipo en la base de datos.

    Parámetros:
    - `user_id` (str): Identificador del usuario.
    - `empresa_id` (str): Identificador de la empresa.
    - `equipo_id` (str, opcional): ID del equipo a filtrar (si se proporciona).
    - `tamanio_pagina` (int, opcional): Tamaño de la página (por defecto 10).
    - `pagina` (int, opcional): Número de la página (por defecto 0).

    Respuesta:
    - `200`: Consulta exitosa.
    - `400`: Error en la operación.
    """
    try:
        # Convertir los parámetros en un diccionario
        params = [{
            'user_id': user_id,
            'empresa_id': empresa_id,
            'bloqueo': bloqueo,
            'equipo_id': equipo_id,
            'integrantes': integrantes,
            'tamanio_pagina': tamanio_pagina,
            'pagina': pagina
        }]
        # Ejecutar la operación en Neo4j
        response = post.ObtenerIntegrantes(params)
        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@query.put("/editar_integrante", tags=['Integrantes'], summary="Editar un integrante")
def editar_integrantes(payload: EditarIntegrante):
    """
    Este endpoint permite editar un integrante en la base de datos.

    Parámetros:
    - `user_id` (str): Identificador del usuario.
    - `empresa_id` (str): Identificador de la empresa.
    - `integrante_id` (str): Identificador del integrante a editar.
    - `equipo_id` (str): Nuevo equipo del integrante.

    Respuesta:
    - `200`: Modificación exitosa.
    - `400`: Error en la operación.
    """
    try:
        # Convertir la carga útil en un diccionario
        data = [payload.model_dump()]
        print(data)
        # Ejecutar la operación en Neo4j
        response = post.EditarIntegrantes(data)
        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
