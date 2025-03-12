COMPRA_ILMITADO_INDIVIDUAL = """
// COBRO ACCESOS ILIMITADOS PERSONAS
UNWIND $data AS record
MATCH (user:jhi_user {user_id: record.user_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)--(empresa:Empresa {id: record.empresa_id})--(equipo:EquipoEmpresa)--(m:Miembros {id:record.integrante_id}),
  (empresa)--(s:SaldosEmpresa),
  (equipo)--(privilegio:PrivilegiosEmpresarial),
  (a:AccesoIlimitado)

SET s.saldo_pendiente = s.saldo_pendiente + a.precio, s.fecha_saldo_pendiente = toString(datetime.truncate('second', datetime({timezone:'America/Bogota'}))), privilegio.acceso_ilimitado_cupo = privilegio.acceso_ilimitado_cupo + 1

WITH DISTINCT m,s,a, empresa

// OBTENER VARIABLES GENERALES
// Get ingresos miembros
OPTIONAL MATCH (m)-[:IngresoToMiembro]-(im:IngresoMiembro)-[:IngresoMiembroToSede]-(sede:SEDE)
WHERE im.tiempo > 0
WITH m, s, a, empresa, SUM(toFloat(COALESCE(im.tiempo, 0))) AS minutos_total

// Get ingresos miembros sedes_count
OPTIONAL MATCH (sedes_count:SEDE)
WHERE sedes_count.Activa = true
WITH m, s, a, empresa, minutos_total, COUNT(sedes_count) AS q_sedes

// Get ingresos miembros sedes
OPTIONAL MATCH (sedes:SEDE)
WHERE sedes.Activa = true
WITH m, s, a, empresa, minutos_total, q_sedes, sedes

OPTIONAL MATCH (m)-[:IngresoToMiembro]-(imm:IngresoMiembro)-[:IngresoMiembroToSede]-(sedes)
WHERE imm.tiempo > 0
WITH m, s, a, empresa, minutos_total, q_sedes, sedes, SUM(toFloat(COALESCE(imm.tiempo, 0))) AS minutos_sede, 
    round(100.0 * duration.between(date({timezone:'America/Bogota'}), 
                     date.truncate('month', date({timezone: 'America/Bogota'})) + duration({months: 1, days: -1})).days / 
                     (duration.between(date.truncate('month', date({timezone: 'America/Bogota'})), 
                     date.truncate('month', date({timezone: 'America/Bogota'})) + duration({months: 1, days: -1})).days + 1), 2) 
       AS remaining_percentage

// Definir porcentaje de minutos por sede
WITH m, s, a, empresa, minutos_total, q_sedes, sedes, minutos_sede,
     CASE
         WHEN minutos_total = 0 THEN 100 / q_sedes
         ELSE minutos_sede * 100 / minutos_total
     END AS p_sede
WHERE p_sede > 0

// Definir el valor de los registros de compra
WITH m, s, empresa, minutos_total, q_sedes, sedes, minutos_sede, p_sede, (p_sede * a.precio) / 100 AS valor

CREATE (rc:RegistroCompra {
       estado: "PENDING",
       fecha_creacion: toString(datetime.truncate('second', datetime({timezone:'America/Bogota'}))),
       fecha_pago: "",
       id: randomUUID(),
       pagado: false,
       tipo: "acceso_ilimitado_equipo",
       tipo_pago: "saldo_pendiente",
       valor: valor
    })
MERGE (m)<-[:DetalleCompraEquipoToMiembro]-(rc)
MERGE (empresa)<-[:DetalleCompraEmpresa]-(rc)
MERGE (rc)-[:AccesoIlimitadoToSede]->(sedes)
MERGE (rc)-[:MetodoPagoPrepagoConsumo]->(s)
WITH m, rc, sedes, empresa
RETURN collect(rc.id) AS compras
"""

def compra_ilimitado_individual(data, tx):
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
        print( 'estoy entrando a utils', data)
        result = tx.run(COMPRA_ILMITADO_INDIVIDUAL, {'data': data})
        result = result.data()
        print('✔ Los equipos se han importado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')
    
COMPRA_ILMITADO_EQUIPO = """
// COBRO ACCESOS ILIMITADOS EMPRESAS
UNWIND $data AS record

MATCH (user:jhi_user {user_id:record.user_id})--(adm:Miembros)--(aem:AdministradorEmpresa)--(e:Empresa {id:record.empresa_id})-[:EmpresaToSaldo]-(s:SaldosEmpresa),
    (e)-[:EmpresaToEquipo]-(eq:EquipoEmpresa {id:record.equipo_id})-[:PrivilegiosEquipoEmpresa]-(p:PrivilegiosEmpresarial)
OPTIONAL MATCH (eq)-[:EquipoToMiembro]-(m:Miembros)
OPTIONAL MATCH (m:Miembros)--(b:BloqueoEmpresarial)
WITH user, adm, aem, e, s, eq, p, m, b
SET p.acceso_ilimitado = true, p.accesoi_fecha_inicio = toString(datetime.truncate('second', datetime({timezone:'America/Bogota'})))
WITH user, adm, aem, e, s, eq, p, m, b
MATCH (a:AccesoIlimitado)
WITH DISTINCT user, adm, aem, e, s, eq, p, m, b, a 

WITH e, s, a, eq, p, COLLECT(m) AS miembros
SET s.saldo_pendiente = s.saldo_pendiente + (a.precio * SIZE(miembros)),  p.acceso_ilimitado_cupo = SIZE(miembros)
WITH e, s, a, eq, p, miembros
// OBTENER VARIABLES GENERALES
// Get ingresos miembros
OPTIONAL MATCH (e)-[:DetalleCompraEmpresa]-(rc:RegistroCompra)-[:DetalleCompra]-(im:IngresoMiembro)
WHERE im.tiempo > 0
WITH e, s, a, eq, p, miembros, SUM(toFloat(COALESCE(im.tiempo, 0))) AS minutos_total
// Get ingresos miembros sedes_count
OPTIONAL MATCH (sedes_count:SEDE)
WHERE sedes_count.Activa = true
WITH e, s, a, eq, p, miembros, minutos_total, COUNT(sedes_count) AS q_sedes
// Get ingresos miembros sedes
OPTIONAL MATCH (sedes:SEDE)
WHERE sedes.Activa = true
WITH e, s, a, eq, p, miembros, minutos_total, q_sedes, sedes
OPTIONAL MATCH (e)-[:DetalleCompraEmpresa]-(rc:RegistroCompra)-[:DetalleCompra]-(imm:IngresoMiembro)-[:IngresoMiembroToSede]-(sedes)
WHERE imm.tiempo > 0
WITH e, s, a, eq, p, miembros, minutos_total, q_sedes, sedes, SUM(toFloat(COALESCE(imm.tiempo, 0))) AS minutos_sede

// Definir porcentaje de minutos por sede
WITH e, s, a, eq, p, miembros, minutos_total, q_sedes, sedes, minutos_sede,
     CASE
         WHEN minutos_total = 0 THEN 100 / q_sedes
         ELSE minutos_sede * 100 / minutos_total
     END AS p_sede
WHERE p_sede > 0

// Definir el valor de los registros de compra
WITH e, s, a, eq, p, miembros, minutos_total, q_sedes, sedes, minutos_sede, p_sede, (p_sede * a.precio * SIZE(miembros)) / 100 AS valor
WHERE valor > 0.0
CREATE (rc:RegistroCompra {
       estado: "PENDING",
       fecha_creacion: toString(datetime.truncate('second', datetime({timezone:'America/Bogota'}))),
       fecha_pago: toString(datetime.truncate('second', datetime({timezone:'America/Bogota'}))),
       id: randomUUID(),
       pagado: false,
       tipo: "acceso_ilimitado_equipo",
       tipo_pago: "saldo_pendiente",
       valor: valor
    })
MERGE (rc)-[:AccesoIlimitadoToSede]->(sedes)
MERGE (rc)-[:DetalleCompraEmpresa]->(e)
MERGE (rc)-[:DetalleCompraEmpresaSaldo]->(s)
WITH rc, e, s, miembros
UNWIND miembros AS miembro
MERGE (miembro)<-[:DetalleCompraEquipoToMiembro]-(rc)
WITH rc, e, s, miembros
RETURN COLLECT( DISTINCT rc.id) AS compras
"""

def compra_ilimitado_equipo(data, tx):
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
        print( 'estoy entrando a utils', data)
        result = tx.run(COMPRA_ILMITADO_EQUIPO, {'data': data})
        result = result
        print('✔ Los equipos se han importado correctamente. ', result)
        return result.data()
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')
    

COMPRA_MEMBRESIA_EQUIPO = """
UNWIND $data AS record
MATCH (user:jhi_user {user_id:record.user_id})--(adm:Miembros)--(aem:AdministradorEmpresa)--(e:Empresa {id:record.empresa_id})-[:EmpresaToSaldo]-(s:SaldosEmpresa),
    (e)-[:EmpresaToEquipo]-(eq:EquipoEmpresa {id:record.equipo_id})-[:PrivilegiosEquipoEmpresa]-(p:PrivilegiosEmpresarial)
OPTIONAL MATCH (eq)-[:EquipoToMiembro]-(m:Miembros)
OPTIONAL MATCH (m:Miembros)--(b:BloqueoEmpresarial {bloqueo:false})
WITH user, adm, aem, e, s, eq, p, COLLECT(m) AS miembros
SET p.membresia = true, p.membresia_fecha_inicio = toString(datetime.truncate('second', datetime({timezone:'America/Bogota'}))), p.membresia_cupo = SIZE(miembros)
WITH user, adm, aem, e, s, eq, p, miembros
MATCH (n:NivelEmpresarial {id:'a01f20e9-8c3b-4a81-95d4-00b46a9ecc22'})
WITH DISTINCT user, adm, aem, e, s, eq, p, n, miembros
WITH e, s, eq, p, n, miembros
WHERE SIZE(miembros) > 0

CREATE (rc:RegistroCompra {
       estado: "PENDING",
       fecha_creacion: toString(datetime.truncate('second', datetime({timezone:'America/Bogota'}))),
       fecha_pago: toString(datetime.truncate('second', datetime({timezone:'America/Bogota'}))),
       id: randomUUID(),
       pagado: false,
       tipo: "suscripcion_empresa",
       tipo_pago: "saldo_pendiente",
       valor: n.valor_nivel * SIZE(miembros)
    })
MERGE (rc)-[:DetalleCompraEmpresa]->(e)
MERGE (rc)-[:DetalleCompraEmpresaSaldo]->(s)
WITH rc, e, s, miembros, n
UNWIND miembros AS miembro
MATCH (miembro)-[l1]-(:NivelEmpresarial)
DELETE l1
MERGE (miembro)<-[:NivelToEmpresa]-(n)
MERGE (miembro)<-[:DetalleCompraEquipoToMiembro]-(rc)
WITH rc, e, s, miembros
RETURN COLLECT( DISTINCT rc.id) AS compras
"""

def compra_membresia_equipo(data, tx):
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
        print( 'estoy entrando a utils', data)
        result = tx.run(COMPRA_MEMBRESIA_EQUIPO, {'data': data})
        result = result.data()
        print('✔ Los equipos se han importado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')
    

OBTENER_COMPRAS = """
UNWIND $data AS record

MATCH (user:jhi_user {user_id: record.user_id})
      --(miembro:Miembros)
      --(admin:AdministradorEmpresa)
      --(empresa:Empresa {id: record.empresa_id})
      --(compra:RegistroCompra)

WHERE (record.pagado IS NULL OR compra.pagado = record.pagado)

OPTIONAL MATCH (compra)--(integrante:Miembros)--(eq:EquipoEmpresa)
OPTIONAL MATCH (integrante)--(bloqueo:BloqueoEmpresarial)
OPTIONAL MATCH (s_miembro:SEDE)--(ing_miembro:IngresoMiembro)--(compra)
OPTIONAL MATCH (s_invitado:SEDE)--(ing_invitado:IngresoInvitado)--(compra)
OPTIONAL MATCH (s_express:SEDE)--(ingreso_express:IngresoInvitacionExpress)--(compra)
OPTIONAL MATCH (s_reserva:SEDE)--(er:EspacioReserva)--(reserva:Reservas)--(compra)
OPTIONAL MATCH (compra)--(s_otro:SEDE)
WITH DISTINCT 
    compra, 
    COLLECT({
        id: integrante.id, 
        identificacion: integrante.identificacion, 
        nombre: trim(integrante.nombre), 
        correo: trim(integrante.login)
    }) AS integrantes,

    CASE 
        WHEN ing_miembro IS NOT NULL AND ing_miembro.hora_entrada IS NOT NULL
        THEN toString(datetime({
            epochSeconds: timestamp(ing_miembro.hora_entrada)/1000, 
            timezone: 'America/Bogota'
        }))
        WHEN ing_invitado IS NOT NULL AND ing_invitado.hora_entrada IS NOT NULL
        THEN toString(datetime({
            epochSeconds: timestamp(ing_invitado.hora_entrada)/1000, 
            timezone: 'America/Bogota'
        }))
        WHEN ingreso_express IS NOT NULL AND ingreso_express.hora_entrada IS NOT NULL
        THEN toString(datetime({
            epochSeconds: timestamp(ingreso_express.hora_entrada)/1000, 
            timezone: 'America/Bogota'
        }))
        WHEN reserva IS NOT NULL AND reserva.fecha_entrada IS NOT NULL
        THEN toString(datetime({
            epochSeconds: timestamp(reserva.fecha_entrada)/1000, 
            timezone: 'America/Bogota'
        }))
        ELSE "" 
    END AS hora_entrada,

    CASE 
        WHEN ing_miembro IS NOT NULL AND ing_miembro.hora_salida IS NOT NULL
        THEN toString(datetime({
            epochSeconds: timestamp(ing_miembro.hora_salida)/1000, 
            timezone: 'America/Bogota'
        }))
        WHEN ing_invitado IS NOT NULL AND ing_invitado.hora_salida IS NOT NULL
        THEN toString(datetime({
            epochSeconds: timestamp(ing_invitado.hora_salida)/1000, 
            timezone: 'America/Bogota'
        }))
        WHEN ingreso_express IS NOT NULL AND ingreso_express.hora_salida IS NOT NULL
        THEN toString(datetime({
            epochSeconds: timestamp(ingreso_express.hora_salida)/1000, 
            timezone: 'America/Bogota'
        }))
        WHEN reserva IS NOT NULL AND reserva.fecha_salida IS NOT NULL
        THEN toString(datetime({
            epochSeconds: timestamp(reserva.fecha_salida)/1000, 
            timezone: 'America/Bogota'
        }))
        ELSE "" 
    END AS hora_salida,

    COALESCE(s_miembro.nombre_sede, s_invitado.nombre_sede, s_express.nombre_sede, s_reserva.nombre_sede + ' : ' + er.nombre, s_otro.nombre_sede, "NEWO") AS sede, 
    datetime({
        epochSeconds: timestamp(compra.fecha_pago)/1000, 
        timezone: 'America/Bogota'
    }) AS fecha_compra, 
    compra.fecha_pago AS fecha_compra_filtro,

    COALESCE(record.filtro, "") AS filtro_busqueda,
    CASE 
        WHEN record.fecha_inicio IS NOT NULL THEN record.fecha_inicio 
        ELSE NULL 
    END AS filtro_fecha_inicio,
    CASE 
        WHEN record.fecha_fin IS NOT NULL THEN record.fecha_fin 
        ELSE NULL 
    END AS filtro_fecha_fin,
    COALESCE(record.sede, "") AS filtro_sede,
    
    COALESCE(record.tamanio_pagina, 10) AS tamanio_pagina, 
    COALESCE(record.pagina, 0) AS pagina

// Filtrar por coincidencia en nombre o correo de algún integrante
WITH compra, integrantes, hora_entrada, hora_salida, sede, fecha_compra, filtro_busqueda, 
     filtro_fecha_inicio, filtro_fecha_fin, filtro_sede, fecha_compra_filtro, tamanio_pagina, pagina,
     (filtro_busqueda = "" OR ANY(i IN integrantes WHERE i.nombre CONTAINS filtro_busqueda OR i.correo CONTAINS filtro_busqueda)) AS tiene_coincidencia

// Aplicar los filtros adicionales correctamente
WHERE tiene_coincidencia 
  AND (filtro_sede = "" OR LOWER(sede) CONTAINS LOWER(filtro_sede)) 
  AND (filtro_fecha_inicio IS NULL OR toString(fecha_compra_filtro) >= filtro_fecha_inicio)
  AND (filtro_fecha_fin IS NULL OR toString(fecha_compra_filtro) <= filtro_fecha_fin)

WITH DISTINCT {
    id: compra.id,
    pagado: compra.pagado,
    valor: round(toFloat(compra.valor), 2),
    tipo: compra.tipo,
    fecha_compra: toString(fecha_compra),
    hora_entrada: hora_entrada,
    hora_salida: hora_salida,
    sede: sede,
    integrantes: integrantes
} AS compra_data, fecha_compra, tamanio_pagina, pagina

// Ordenar todas las compras por fecha
ORDER BY fecha_compra DESC

// Contar el total de resultados para metadata
WITH COLLECT(compra_data) AS todas_compras, tamanio_pagina, pagina
WITH todas_compras, tamanio_pagina, pagina,
     SIZE(todas_compras) AS total_registros

// Aplicar la paginación a la lista completa de compras
RETURN {
    registros: total_registros,
    tamanio_pagina: tamanio_pagina,
    pagina: pagina,
    total_paginas: CASE 
                    WHEN total_registros = 0 THEN 0
                    ELSE CEIL(toFloat(total_registros) / tamanio_pagina)
                   END
} AS metadata,
[i IN RANGE(pagina * tamanio_pagina, (pagina + 1) * tamanio_pagina - 1) 
    WHERE i < SIZE(todas_compras) | todas_compras[i]] AS compras
"""

def obtener_compras(data, tx):
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
        print( 'estoy entrando a utils', data)
        result = tx.run(OBTENER_COMPRAS, {'data': data})
        result = result.data()
        print('✔ Los equipos se han importado correctamente.')
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')