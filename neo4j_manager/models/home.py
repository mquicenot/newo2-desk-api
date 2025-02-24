# Consulta para obtener información de un usuario y su relación con la empresa
ONTENER_EMPRESAS_ADMIN = """
    UNWIND $data AS record
    MATCH (miembro_solo:Miembros {login:record.email})
    OPTIONAL MATCH (usuario:jhi_user {user_id:record.auth_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)--(empresa:Empresa)
    WITH usuario, miembro, empresa, miembro_solo
    RETURN
    {
        login:usuario.login,
        auth_id:usuario.user_id
    } AS usuario,
    {
        id:miembro.id,
        nombre:miembro.nombre,
        tipo_documento:miembro.tipo_documento,
        documento:miembro.identificacion,
        email:miembro.login,
        activo:miembro.activo
    } AS perfil,
    {
        id:miembro_solo.id,
        nombre:miembro_solo.nombre,
        tipo_documento:miembro_solo.tipo_documento,
        documento:miembro_solo.identificacion,
        email:miembro_solo.login,
        activo:miembro_solo.activo
    } AS perfil_solo,
    {
        id:empresa.id,
        razon_social:empresa.razon_social,
        documento:empresa.nit
    } AS empresa
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
        print("📥 Datos de entrada:", data)
        result = tx.run(INIT_COMPONENTS, {'data': data})
        result = result.data()
        print("✔ Usuarios obtenidos correctamente:", result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al obtener usuarios: {str(e)}')