from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel, Field
from neo4j_manager.utils.membresias import Neo4jMembresias  # Clase para interactuar con Neo4j

# Se crea un router de FastAPI para definir los endpoints de esta sección
query = APIRouter()

# Instancia de la clase para realizar operaciones en Neo4j
post = Neo4jMembresias()

@query.get("/obtener_membresias", tags=['Membresias'], summary="Obtener membresias en la base de datos")
def obtener_integrantes():
    """
    Este endpoint permite consultar los integrantes de un equipo en la base de datos.

    Parámetros:
    - No aplican

    Respuesta:
    - `200`: Consulta exitosa.
    - `400`: Error en la operación.
    """
    try:
        # Ejecutar la operación en Neo4j
        response = post.ObtenerMembresias()
        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))