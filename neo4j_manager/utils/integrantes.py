from neo4j_manager.models.integrantes import obtener_integrantes, editar_integrantes, invitar_integrante_crear, invitar_integrante_unir
from neo4j_manager.models.init_components import usuario_info
from neo4j_manager.driver import Neo4jDriver
from auth0_manager.requests import auth0Services
import random
import string


class Neo4jIntegrantes:
    """
    Procesar solicitudes POST de usuarios para creación en Neo4j.
    """

    def __init__(self):
        """
        Constructor de la clase. Inicializa las conexiones a la base de datos.
        """
        self.db = Neo4jDriver()

    def ObtenerIntegrantes(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    result = obtener_integrantes(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    print(f"❌ Error al ejecutar la mutación: {e}")
                    tx.rollback()
                finally:
                    self.db.close()
    
    
    def EditarIntegrantes(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    result = editar_integrantes(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    print(f"❌ Error al ejecutar la mutación: {e}")
                    tx.rollback()
                finally:
                    self.db.close()
                    
                    
    def InvitarIntegrante(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Lista de diccionarios que contienen la información de los usuarios a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    for x in user_data:
                        email = x.get('email_integrante')  # Evita errores si la clave no existe
                        if not email:
                            print("⚠ Advertencia: No se proporcionó un email válido.")
                            continue

                        print('📌 Procesando usuario:', x)
                        print('📧 Email:', email)

                        try:
                            # Generar contraseña y crear usuario en Auth0
                            password = self.generar_contrasena()
                            result = auth0Services().create_new_user(email, password)
                            print('✔ Usuario creado correctamente en Auth0:', result)

                        except Exception as e:
                            print(f"⚠ Error creando usuario en Auth0: {e}")

                        # Verificar si el usuario ya existe en Neo4j
                        perfil = usuario_info([{'email_integrante': email}], tx)
                        print('📊 Información del perfil:', perfil or 'No hay datos'   )
                        if perfil:
                            equipo = perfil[0]['equipo']['id']
                            if not (equipo == None):
                                raise Exception(f"❌ El usuario {email} ya cuenta con equipo.")
                            else:
                                print('🔗 Usuario sin equipo, lo voy a vincular.')
                                invitar_integrante_unir([x], tx)

                        else:
                            print("➕ Usuario no encontrado en Neo4j, se procederá a crearlo y unir a equipo.")
                            invitar_integrante_crear([x], tx)


                        print('📊 Información del perfil:', perfil or 'No hay datos')
                        tx.commit()
                        return 'El ususario se ha vincula exitosamente'

                except Exception as e:
                    print(f"❌ Error al ejecutar la mutación en Neo4j: {e}")
                    tx.rollback()
                    return 'Ha ocurrido un error al vincular al integrante'
                finally:
                    self.db.close()

    def generar_contrasena(self):
        mayuscula = random.choice(string.ascii_uppercase)
        numero = random.choice(string.digits)
        especial = random.choice("!@#$%^&*()-_=+")
        resto = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()-_=+", k=5))

        # Mezclar los caracteres para evitar patrones predecibles
        contrasena = list(mayuscula + numero + especial + resto)
        random.shuffle(contrasena)

        return ''.join(contrasena)