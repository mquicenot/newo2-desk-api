COMPRA_ILMITADO_INDIVIDUAL = """
// COBRO ACCESOS ILIMITADOS PERSONAS
UNWIND $data AS record
MATCH (user:jhi_user {user_id: record.user_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)--(empresa:Empresa {id: record.empresa_id})--(equipo:EquipoEmpresa)--(m:Miembros {id:record.integrante_id}),
  (empresa)--(s:SaldosEmpresa),
  (a:AccesoIlimitado)

SET s.saldo_pendiente = s.saldo_pendiente + a.precio, s.fecha_saldo_pendiente = toString(datetime({timezone:'America/Bogota'}))

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
       fecha_creacion: toString(datetime({timezone:'America/Bogota'})),
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
    