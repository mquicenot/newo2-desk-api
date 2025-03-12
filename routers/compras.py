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

class AccesoIlimitadoEquipo(BaseModel):
    user_id: str = Field(..., description="ID único del usuario que realiza la acción.")
    empresa_id: str = Field(..., description="ID de la empresa a la que pertenece el usuario.")
    equipo_id: str = Field(..., description="ID del equipo dentro de la empresa, si aplica.")
    
class MembresiaEquipo(BaseModel):
    user_id: str = Field(..., description="ID único del usuario que realiza la acción.")
    empresa_id: str = Field(..., description="ID de la empresa a la que pertenece el usuario.")
    equipo_id: str = Field(..., description="ID del equipo dentro de la empresa, si aplica.")
    

@query.get("/cotizar_valor", tags=['Compras'], summary="Cotiza el valor de tu compra: ilimitado equipo, ilimitado individual")
def cotizar_valor(payload: CompraIlimitadoIndividual):
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

from fastapi import Query

from fastapi import Query
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi import HTTPException

@query.get("/obtener_compras", tags=['Compras'], summary="Obtiene compras con filtros aplicados")
def obtener_compras(
    user_id: str = Query(..., description="ID del usuario que realiza la consulta."),
    empresa_id: str = Query(..., description="ID de la empresa asociada a las compras."),
    filtro: Optional[str] = Query(None, description="Texto para filtrar por nombre o correo de los integrantes."),
    fecha_inicio: Optional[str] = Query(None, description="Fecha mínima de compra en formato 'YYYY-MM-DDTHH:mm:ss'."),
    fecha_fin: Optional[str] = Query(None, description="Fecha máxima de compra en formato 'YYYY-MM-DDTHH:mm:ss'."),
    sede: Optional[str] = Query(None, description="Texto para filtrar por el nombre de la sede."),
    tamanio_pagina: Optional[int] = Query(5, description="Cantidad de registros por página (por defecto 10)."),
    pagina: Optional[int] = Query(0, description="Número de página a recuperar (inicio en 0 por defecto)."),
    pagado: Optional[bool] = Query(None, description="Número de página a recuperar (inicio en 0 por defecto).")
):
    """
    Este endpoint permite obtener compras con filtros.

    Parámetros:
    - `user_id` (str, obligatorio): Identificador del usuario.
    - `empresa_id` (str, obligatorio): Identificador de la empresa.
    - `filtro` (str, opcional): Filtrar por nombre o correo de integrantes.
    - `fecha_inicio` (str, opcional): Fecha mínima (YYYY-MM-DDTHH:mm:ss).
    - `fecha_fin` (str, opcional): Fecha máxima (YYYY-MM-DDTHH:mm:ss).
    - `sede` (str, opcional): Filtrar por nombre de la sede.
    - `tamanio_pagina` (int, opcional): Tamaño de página, por defecto 5.
    - `pagina` (int, opcional): Número de página, inicia en 0.

    Respuesta:
    - `200`: Retorna la lista de compras filtradas.
    - `400`: Error en la operación.
    """
    try:
        # Crear el diccionario solo con valores que no sean None
        records = {
            "user_id": user_id,
            "empresa_id": empresa_id,
            "filtro": filtro,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "sede": sede,
            "tamanio_pagina": tamanio_pagina,
            "pagina": pagina,
            "pagado":pagado
        }
        
        # Filtrar valores None
        records = {key: value for key, value in records.items() if value is not None}

        print(records)  # Debug

        # Ejecutar la operación en Neo4j
        response = post.ObtenerCompras([records])

        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@query.post("/ilimitado_individual", tags=['Compras'], summary="Comprar acceso ilmitado para una persona.")
def ilimitado_individual(payload: CompraIlimitadoIndividual):
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
        records = [payload.model_dump]
        
        print(records)
        
        # Ejecutar la operación en Neo4j
        response = post.IlimitadoIndividual(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@query.post("/ilimitado_equipo", tags=['Compras'], summary="Comprar acceso ilmitado para una persona.")
def ilimitado_equipo(payload: AccesoIlimitadoEquipo):
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
        records = [payload.model_dump()]
        
        print(records)
        
        # Ejecutar la operación en Neo4j
        response = post.IlimitadoEquipo(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@query.post("/membresia_equipo", tags=['Compras'], summary="Comprar acceso ilmitado para una persona.")
def membresia_equipo(payload: MembresiaEquipo):
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
        records = [payload.model_dump()]
        
        print(records)
        
        # Ejecutar la operación en Neo4j
        response = post.MembresiaEquipo(records)

        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))