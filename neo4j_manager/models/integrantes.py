OBTENER_INTEGRANTES = """
UNWIND $data AS record
MATCH (user:jhi_user {user_id: record.user_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)
      --(empresa:Empresa {id: record.empresa_id})--(equipo:EquipoEmpresa)--(privilegio:PrivilegiosEmpresarial),
      (equipo)--(integrante:Miembros),
      (bloqueo:BloqueoEmpresarial)--(integrante)--(nivel:NivelEmpresarial),
      (integrante)--(compras:RegistroCompra)--(empresa)
WHERE (record.bloqueo IS NULL OR bloqueo.bloqueo = record.bloqueo)
    AND (record.equipo_id IS NULL OR equipo.id = record.equipo_id) 
    AND (
        record.integrantes IS NULL 
        OR (
            record.integrantes IS NOT NULL 
            AND (
                LOWER(integrante.login) CONTAINS LOWER(record.integrantes) 
                OR LOWER(integrante.identificacion) CONTAINS LOWER(record.integrantes) 
                OR LOWER(integrante.nombre) CONTAINS LOWER(record.integrantes)
            )
        )
    )

ORDER BY integrante.correo ASC
WITH record.tamanio_pagina AS tamanio_pagina, record.pagina AS pagina, 
     integrante, COLLECT(compras) AS compras, bloqueo, nivel, equipo, privilegio, empresa
WITH {
    id: integrante.id,
    bloqueo: {
        bloqueo: bloqueo.bloqueo, 
        bloqueo_fecha_inicio: bloqueo.bloqueo_fecha_inicio, 
        bloqueo_fecha_fin: bloqueo.bloqueo_fecha_fin,
        bloqueo_fecha_fin_dias: 
            CASE 
                WHEN bloqueo.bloqueo_fecha_fin IS NOT NULL 
                THEN duration.between(
                    datetime(), 
                    COALESCE(
                        CASE 
                            WHEN bloqueo.bloqueo_fecha_fin =~ '\\d{13}' 
                            THEN datetime(apoc.date.format(toInteger(bloqueo.bloqueo_fecha_fin), 'ms', "yyyy-MM-dd'T'HH:mm:ss")) 
                            WHEN bloqueo.bloqueo_fecha_fin =~ '\\d{10}' 
                            THEN datetime(apoc.date.format(toInteger(bloqueo.bloqueo_fecha_fin), 's', "yyyy-MM-dd'T'HH:mm:ss")) 
                            ELSE datetime(replace(bloqueo.bloqueo_fecha_fin, ' ', 'T')) 
                        END, 
                        datetime()
                    )
                ).days 
                ELSE NULL 
            END
    },
    nombre: integrante.nombre,
    documento: integrante.identificacion,
    tipo_documento: integrante.tipo_documento,
    fecha_nacimiento: SUBSTRING(integrante.fecha_nacimiento, 0, 10),
    correo: integrante.login,
    genero: integrante.genero,
    privilegios: {
        oficina: privilegio.oficina,
        acceso_ilimitado: privilegio.acceso_ilimitado,
        acceso_ilimitado_fecha_inicio: COALESCE(toString(privilegio.accesoi_fecha_inicio), ""),
        acceso_ilimitado_fecha_fin: COALESCE(toString(privilegio.accesoi_fecha_fin), ""),
        pago_reservas: privilegio.pago_reservas,
        pago_invitados: privilegio.pago_invitados,
        tope_ingreso_miembros: privilegio.ingreso_sede,
        tope_ingresos_invitados: privilegio.invitados,
        tope_ingresos_reservas: privilegio.eventos
    },
    equipo: {
        id: equipo.id,
        nombre: equipo.nombre
    },
    nivel: {
        id: nivel.id,
        nombre: nivel.nombre
    }
} AS integrante, pagina, tamanio_pagina

WITH COLLECT(integrante) AS integrantes, tamanio_pagina, pagina

// Calcular metadata antes de la paginación
WITH integrantes, tamanio_pagina, pagina, 
     { registros: SIZE(integrantes), tamanio_pagina: tamanio_pagina, pagina: pagina } AS metadata

//// Paginación manual sin usar `CALL {}`
WITH metadata, integrantes, tamanio_pagina, pagina
RETURN metadata, 
       [i IN RANGE(pagina * tamanio_pagina, (pagina + 1) * tamanio_pagina - 1) 
        WHERE i < SIZE(integrantes) | integrantes[i]] AS integrantes
"""

def obtener_integrantes(data, tx):
    """
    Función para crear un nuevo usuario en la base de datos Neo4j.
    Ejecuta una consulta Cypher para insertar un usuario si no existe, o actualizarlo si ya está presente.

    :param data: Una lista de diccionarios que contiene la información del usuario. Cada diccionario debe tener 
                 las claves 'email', 'name'.
    :param tx: El objeto de transacción de Neo4j que se utiliza para ejecutar la consulta Cypher.

    :return: Una lista de resultados de la consulta, indicando los usuarios que se han insertado o actualizado.
    
    :raises ValueError: Si ocurre un error al ejecutar la consulta.
    """
    try:
        result = tx.run(OBTENER_INTEGRANTES, {'data': data})
        result = result.data()
        print('✔ Los integrantes se han importado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')
    
    
EDITAR_INTEGRANTES = """
UNWIND $data AS record
MATCH (user:jhi_user {user_id: record.user_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)
      --(empresa:Empresa {id: record.empresa_id})--(equipo:EquipoEmpresa)--(privilegio:PrivilegiosEmpresarial),
      (equipo)-[l1]-(integrante:Miembros),
      (bloqueo:BloqueoEmpresarial)--(integrante)--(nivel:NivelEmpresarial),
      (integrante {id: record.integrante_id})--(compras:RegistroCompra)--(empresa), 
      (equipo_to:EquipoEmpresa {id: record.equipo_id})
WITH DISTINCT integrante, equipo, equipo_to, bloqueo, record, l1,
  CASE 
    WHEN bloqueo.bloqueo = true 
      AND record.bloqueo = false 
      AND datetime(bloqueo.bloqueo_fecha_fin) <= datetime({timezone:'America/Bogota'})
      THEN false 
    WHEN bloqueo.bloqueo = false 
      AND record.bloqueo = true 
      THEN true 
    ELSE bloqueo.bloqueo 
  END AS nuevo_bloqueo,
  CASE 
    WHEN bloqueo.bloqueo = false 
      AND record.bloqueo = true 
      THEN toString(datetime({timezone: 'America/Bogota'}) + duration({days:30}))
    WHEN bloqueo.bloqueo = true 
      AND record.bloqueo = false 
      AND datetime(bloqueo.bloqueo_fecha_fin) <= datetime({timezone:'America/Bogota'})
      THEN null
    ELSE toString(bloqueo.bloqueo_fecha_fin)
  END AS nuevo_bloqueo_fecha_fin,
  CASE 
    WHEN bloqueo.bloqueo = false 
      AND record.bloqueo = true 
      THEN toString(datetime({timezone: 'America/Bogota'}))
    WHEN bloqueo.bloqueo = true 
      AND record.bloqueo = false 
      AND datetime(bloqueo.bloqueo_fecha_fin) <= datetime({timezone:'America/Bogota'})
      THEN null
    ELSE toString(bloqueo.bloqueo_fecha_inicio)
  END AS nuevo_bloqueo_fecha_inicio

// Eliminar la relación si existe
FOREACH (_ IN CASE WHEN l1 IS NOT NULL THEN [1] ELSE [] END | DELETE l1)

MERGE (integrante)<-[:EquipoToMiembro]-(equipo_to)
SET bloqueo.bloqueo = nuevo_bloqueo,
    bloqueo.bloqueo_fecha_fin = nuevo_bloqueo_fecha_fin,
    bloqueo.bloqueo_fecha_inicio = nuevo_bloqueo_fecha_inicio
RETURN integrante.id AS integrante, bloqueo.bloqueo AS bloqueo, bloqueo.bloqueo_fecha_inicio AS bloqueo_inicio, bloqueo.bloqueo_fecha_fin AS bloqueo_fin
"""

def editar_integrantes(data, tx):
    """
    Función para crear un nuevo usuario en la base de datos Neo4j.
    Ejecuta una consulta Cypher para insertar un usuario si no existe, o actualizarlo si ya está presente.

    :param data: Una lista de diccionarios que contiene la información del usuario. Cada diccionario debe tener 
                 las claves 'email', 'name'.
    :param tx: El objeto de transacción de Neo4j que se utiliza para ejecutar la consulta Cypher.

    :return: Una lista de resultados de la consulta, indicando los usuarios que se han insertado o actualizado.
    
    :raises ValueError: Si ocurre un error al ejecutar la consulta.
    """
    try:
        result = tx.run(EDITAR_INTEGRANTES, {'data': data})
        result = result.data()
        print('✔ Los integrantes se han importado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')