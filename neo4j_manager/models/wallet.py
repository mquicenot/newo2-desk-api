OBTENER_METODOS_PAGO = """
UNWIND $data AS record

MATCH (user:jhi_user {user_id: record.user_id})
      --(miembro:Miembros)
      --(admin:AdministradorEmpresa)
      --(empresa:Empresa {id: record.empresa_id})
      --(saldos:SaldosEmpresa)

OPTIONAL MATCH (empresa)--(tarjeta:TarjetaAsociada)
WHERE tarjeta.estado = 'AVAILABLE'

WITH {
  id: saldos.id,
  saldo_recarga: toInteger(saldos.saldo_recarga),
  saldo_bono: toInteger(saldos.saldo_bono),
  saldo_credito: toInteger(saldos.saldo_credito)
} AS saldos, 
COLLECT (DISTINCT{
  id: tarjeta.id,
  mes_vencimiento: tarjeta.exp_month,
  anio_vencimiento: tarjeta.exp_year,
  nombre: tarjeta.name,
  numero: tarjeta.numero_tarjeta,
  franquicia: tarjeta.franquicia,
  correo: tarjeta.correo_cliente,
  titular: tarjeta.titular,
  token: tarjeta.token,
  favorita: tarjeta.favorita
}) AS tarjetas

RETURN *;

"""

def obtener_metodos_pago(data, tx):
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
        result = tx.run(OBTENER_METODOS_PAGO, {'data': data})
        result = result.data()
        print('✔ Los equipos se han importado correctamente.')
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')
    

ELIMINAR_TARJETA = """
UNWIND $data AS record

MATCH (user:jhi_user {user_id: record.user_id})
      --(miembro:Miembros)
      --(admin:AdministradorEmpresa)
      --(empresa:Empresa {id: record.empresa_id})
      --(tarjeta:TarjetaAsociada {id: record.tarjeta_id})

SET tarjeta.estado = 'DESACTIVATED'
RETURN COLLECT(DISTINCT{id:tarjeta.id}) AS tarjetas
"""

def eliminar_tarjeta(data, tx):
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
        result = tx.run(ELIMINAR_TARJETA, {'data': data})
        result = result.data()
        print('✔ Los equipos se han importado correctamente.', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')