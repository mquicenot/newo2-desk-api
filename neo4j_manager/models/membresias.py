OBTENER_MEMBRESIAS = """
MATCH (nivel:NivelEmpresarial)
WHERE nivel.visible = true
ORDER BY nivel.valor ASC, nivel.usuario_adicional DESC 
WITH COLLECT({
  id:nivel.id,
  nombre: nivel.nombre,
  valor: nivel.valor_nivel,
  descuento: nivel.descuento_sede,
  min_usuarios: nivel.min_rango_empresa,
  max_usuarios: nivel.max_rango_empresa,
  adicioanl_usuarios: CASE WHEN nivel.usuario_adicional IS NOT NULL THEN true ELSE false END,
  adicional_usuarios_valor: COALESCE(nivel.usuario_adicional, 0)
}) AS niveles_empresa

RETURN *
"""

def obtener_membresias(tx):
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
        result = tx.run(OBTENER_MEMBRESIAS, {})
        result = result.data()
        print('✔ Los equipos se han importado correctamente. ', result)
        return result
    except Exception as e:
        raise ValueError(f'❌ Error al crear o actualizar usuarios: {str(e)}')
    