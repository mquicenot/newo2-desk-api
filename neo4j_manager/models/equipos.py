OBTENER_EQUIPOS = """
UNWIND $data AS record
MATCH (user:jhi_user {user_id:record.auth_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)--(empresa:Empresa)--(equipo:EquipoEmpresa)--(privilegio:PrivilegiosEmpresarial)--(t:TarjetaAsociada)
WITH record, equipo, privilegio,
    CASE 
        WHEN record.acceso_ilimitado IS NULL THEN privilegio.acceso_ilimitado
        WHEN record.acceso_ilimitado = privilegio.acceso_ilimitado THEN privilegio.acceso_ilimitado
        WHEN record.acceso_ilimitado = true THEN privilegio.acceso_ilimitado
        ELSE true END AS cambio_acceso_ilimitado,
    CASE 
        WHEN record.acceso_ilimitado IS NULL THEN privilegio.accesoi_fecha_fin
        WHEN record.acceso_ilimitado = privilegio.acceso_ilimitado THEN privilegio.accesoi_fecha_fin
        WHEN record.acceso_ilimitado = true THEN privilegio.accesoi_fecha_fin
        ELSE datetime({timezone:'America/Bogota', date:datetime.truncate('month', date() + duration({months:1}) - duration({days:1}))})  END AS cambio_acceso_ilimitado_fecha_fin
SET equipo.nombre = toString(record.nombre_equipo),
    equipo.descripcion = toString(COALESCE(record.descripcion, equipo.descripcion)),
    privilegio.pago_invitados = toBoolean(COALESCE(record.pago_invitados, privilegio.pago_invitados)),
    privilegio.pago_reservas = toBoolean(COALESCE(record.pago_reservas, privilegio.pago_reservas)),
    privilegio.acceso_ilimitado = toBoolean(cambio_acceso_ilimitado),
    privilegio.accesoi_fecha_fin = cambio_acceso_ilimitado_fecha_fin
RETURN equipo.id AS equipo_id, equipo.nombre AS nombre_equipo, equipo.descripcion AS descripcion, privilegio.pago_invitados AS pago_invitados, privilegio.pago_reservas AS pago_reservas, privilegio.acceso_ilimitado AS acceso_ilimitado, toString(privilegio.accesoi_fecha_fin) AS acceso_ilimitado_fecha_fin
"""

def modificar_equipos(data, tx):
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
        print(data)
        result = tx.run(MODIFICAR_EQUIPOS, {'data': data})
        result = result.data()
        print('✔ Los usuarios se han creado o actualizado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')
    

MODIFICAR_EQUIPOS = """
UNWIND $data AS record
MATCH (user:jhi_user {user_id:record.auth_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)--(empresa:Empresa)--(equipo:EquipoEmpresa {id:record.equipo_id})--(privilegio:PrivilegiosEmpresarial)
WITH record, equipo, privilegio,
    CASE 
        WHEN record.acceso_ilimitado IS NULL THEN privilegio.acceso_ilimitado
        WHEN record.acceso_ilimitado = privilegio.acceso_ilimitado THEN privilegio.acceso_ilimitado
        WHEN record.acceso_ilimitado = true THEN privilegio.acceso_ilimitado
        ELSE true END AS cambio_acceso_ilimitado,
    CASE 
        WHEN record.acceso_ilimitado IS NULL THEN privilegio.accesoi_fecha_fin
        WHEN record.acceso_ilimitado = privilegio.acceso_ilimitado THEN privilegio.accesoi_fecha_fin
        WHEN record.acceso_ilimitado = true THEN privilegio.accesoi_fecha_fin
        ELSE datetime({timezone:'America/Bogota', date:datetime.truncate('month', date() + duration({months:1}) - duration({days:1}))})  END AS cambio_acceso_ilimitado_fecha_fin
SET equipo.nombre = toString(record.nombre_equipo),
    equipo.descripcion = toString(COALESCE(record.descripcion, equipo.descripcion)),
    privilegio.pago_invitados = toBoolean(COALESCE(record.pago_invitados, privilegio.pago_invitados)),
    privilegio.pago_reservas = toBoolean(COALESCE(record.pago_reservas, privilegio.pago_reservas)),
    privilegio.acceso_ilimitado = toBoolean(cambio_acceso_ilimitado),
    privilegio.accesoi_fecha_fin = cambio_acceso_ilimitado_fecha_fin
RETURN equipo.id AS equipo_id, equipo.nombre AS nombre_equipo, equipo.descripcion AS descripcion, privilegio.pago_invitados AS pago_invitados, privilegio.pago_reservas AS pago_reservas, privilegio.acceso_ilimitado AS acceso_ilimitado, toString(privilegio.accesoi_fecha_fin) AS acceso_ilimitado_fecha_fin
"""

def modificar_equipos(data, tx):
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
        print(data)
        result = tx.run(MODIFICAR_EQUIPOS, {'data': data})
        result = result.data()
        print('✔ Los usuarios se han creado o actualizado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')


CREAR_EQUIPO = """
// Crear equipo empresa
UNWIND $data AS record
MATCH (jhi:jhi_user {user_id: record.auth_id})--(miembro:Miembros)--(administrador:AdministradorEmpresa)--(empresa:Empresa {id: record.empresa_id})

WITH empresa
// Crear el nodo EquipoEmpresa solo si no existe
CREATE (equipo:EquipoEmpresa {
    correo: record.correo,
    descripcion: record.descripcion,
    direccion: '',
    empresa_id_old: '',
    equipo_id_old: '',
    fecha_actualizacion: datetime({timezone: 'America/Bogota'}),
    fecha_creacion: datetime({timezone: 'America/Bogota'}),
    id: randomUUID(),
    nombre: record.nombre,
    pagina_web: '',
    telefono: record.telefono,
    visible: true
})
CREATE (empresa)-[:EmpresaToEquipo]->(equipo)

// Crear nodo SaldoEquipo y relación con EquipoEmpresa
WITH equipo
CREATE (saldo:SaldoEquipo {
    eventos: "0",
    fecha_actualizacion: datetime({timezone: 'America/Bogota'}),
    fecha_creacion: datetime({timezone: 'America/Bogota'}),
    fecha_fin: datetime({timezone: 'America/Bogota'}),
    fecha_inicio: datetime({timezone: 'America/Bogota'}),
    fecha_saldo_pendiente: datetime({timezone: 'America/Bogota'}),
    id: randomUUID(),
    ingreso_sedes: "0",
    invitados: "0",
    market: "0",
    registros: [],
    reservas: "0",
    saldo_pendiente: toFloat(0.0),
    saldo_recarga: toFloat(0.0)
})
CREATE (equipo)-[:EquipoToSaldos]->(saldo)

// Crear nodo PrivilegiosEmpresarial y relación con EquipoEmpresa
WITH equipo, saldo
CREATE (privilegio:PrivilegiosEmpresarial {
    acceso_ilimitado: false,
    consumo_market: false,
    eventos: "sin tope",
    fecha_actualizacion: datetime({timezone: 'America/Bogota'}),
    fecha_creacion: datetime({timezone: 'America/Bogota'}),
    id: randomUUID(),
    ingreso_sede: "sin tope",
    invitados: "sin tope",
    market: "Sin tope",
    oficina: false,
    pago_eventos: false,
    pago_invitados: toBoolean(record.pago_invitados),
    pago_reservas: toBoolean(record.pago_reservas),
    reservas: "sin tope",
    topes: false
})
CREATE (equipo)-[:PrivilegiosEquipoEmpresa]->(privilegio)

RETURN equipo.id
"""

def modificar_equipos(data, tx):
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
        print(data)
        result = tx.run(MODIFICAR_EQUIPOS, {'data': data})
        result = result.data()
        print('✔ Los usuarios se han creado o actualizado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')