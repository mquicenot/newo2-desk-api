# Consulta para obtener información de un usuario y su relación con la empresa
INIT_COMPONENTS = """
UNWIND $data AS record
MATCH (miembro_solo:Miembros {login:record.email})
OPTIONAL MATCH (usuario:jhi_user {user_id:record.auth_id})--(miembro:Miembros)--(admin:AdministradorEmpresa)--(empresa:Empresa)
OPTIONAL MATCH (empresa)--(eq:EquipoEmpresa)--(integrante:Miembros)--(n:NivelEmpresarial)
OPTIONAL MATCH (integrante)--(b:BloqueoEmpresarial)
WITH usuario, miembro, miembro_solo, empresa, 
     COLLECT({integrante: integrante, nivel_id: n.id, nivel_nombre: n.nombre, bloqueo: b.bloqueo}) AS integrantes,
     COLLECT(DISTINCT n.id) AS niveles_empresariales
WITH usuario, miembro, miembro_solo, 
     COLLECT({
         id: empresa.id,
         razon_social: empresa.razon_social,
         documento: empresa.nit,
         integrantes_bloqueados: size([i IN integrantes WHERE i.bloqueo = true]),
         integrantes_activos: size([i IN integrantes WHERE i.bloqueo = false]),
         integrantes_niveles: niveles_empresariales
     }) AS empresas
RETURN {
    login: usuario.login,
    auth_id: usuario.user_id
} AS usuario,
{
    id: miembro.id,
    nombre: miembro.nombre,
    tipo_documento: miembro.tipo_documento,
    documento: miembro.identificacion,
    email: miembro.login,
    activo: miembro.activo
} AS perfil,
{
    id: miembro_solo.id,
    nombre: miembro_solo.nombre,
    tipo_documento: miembro_solo.tipo_documento,
    documento: miembro_solo.identificacion,
    email: miembro_solo.login,
    activo: miembro_solo.activo
} AS perfil_solo,
empresas
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

# Consulta para crear un usuario en jhi_user y asociarlo con un miembro existente
CREATE_JHI_USER_WITH_MIEMBRO = """
    UNWIND $data AS record
    MATCH (miembro:Miembros {login:record.email})
    MERGE (usuario:jhi_user {user_id:record.user_id})<-[:UserToMiembro]-(miembro)
    ON CREATE SET 
        usuario.activated = true,
        usuario.created_date = datetime({timezone:'America/bogota'}),
        usuario.email = record.email,
        usuario.first_name = record.email,
        usuario.lang_key = 'es',
        usuario.last_modified_date = datetime({timezone:'America/bogota'}),
        usuario.last_name = '',
        usuario.login = record.email
    RETURN 'usuario creado'
"""

def create_jhi_user_with_miembro(data, tx):
    """
    Crea un usuario en la tabla jhi_user y lo asocia con un miembro existente en Neo4j.
    
    :param data: Lista de diccionarios con la información del usuario (debe incluir 'email' y 'user_id').
    :param tx: Objeto de transacción de Neo4j para ejecutar la consulta Cypher.
    :return: Lista con el mensaje de éxito si el usuario fue creado.
    :raises ValueError: Si ocurre un error al ejecutar la consulta.
    """
    try:
        print("📥 Datos de entrada:", data)
        result = tx.run(CREATE_JHI_USER_WITH_MIEMBRO, {'data': data})
        result = result.data()
        print("✔ Usuario creado o actualizado correctamente:", result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuario: {str(e)}')
