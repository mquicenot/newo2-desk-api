INIT_COMPONENTS = """
    UNWIND $data AS record
    MATCH (user:jhi_user {user_id:record.auth_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)--(empresa:Empresa)
    RETURN
        CASE WHEN user IS NULL THEN false ELSE true END AS usuario,
        CASE WHEN miembro IS NULL THEN false ELSE true END AS miembro,
        CASE WHEN empresa IS NULL THEN false ELSE true END AS empresa
"""

def init_components(data, tx):
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
        result = tx.run(INIT_COMPONENTS, {'data': data})
        result = result.data()
        print('✔ Los usuarios se han creado o actualizado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')