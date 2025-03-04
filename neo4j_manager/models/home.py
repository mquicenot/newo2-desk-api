# Consulta para obtener información de un usuario y su relación con la empresa
ONTENER_EMPRESAS_ADMIN = """
    UNWIND $data AS record
    MATCH (miembro_solo:Miembros {user_id:record.user_id})
"""

def init_components(data, tx):
    """
    Obtiene la información de un usuario en la base de datos Neo4j, incluyendo sus relaciones con la empresa.
    
    :param data: Lista de diccionarios con la información del usuario (debe incluir 'email' y 'auth_id').
    :param tx: Objeto de transacción de Neo4j para ejecutar la consulta Cypher.
    :return: Lista de diccionarios con la información del usuario y su relación con la empresa.
    :raises ValueError: Si ocurre un error al ejecutar la consulta.
    """
    try:
        result = tx.run(INIT_COMPONENTS, {'data': data})
        result = result.data()
        print("✔ Usuarios obtenidos correctamente:", result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al obtener usuarios: {str(e)}')