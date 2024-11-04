from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from firebase_admin import credentials, firestore, auth, initialize_app
from jose import JWTError, jwt


# Configurando las claves basicas para manipular el acceso a la data.
SECRET_KEY = "pruebatecnica"  # Reemplaza con una clave secreta fuerte
ALGORITHM = "HS256" #Algoritmo de encriptacion que vamos a usar para la API
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #Tiempo en el que vence la sesion de trabajo.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  #  Usaremos esto más adelante

class Usuario(BaseModel):
    username: str
    nombre: str

async def obtener_usuario(username: str):
    # Simula la obtención del usuario de la base de datos
    # En este ejemplo, se devuelve un usuario ficticio si el nombre de usuario es "testuser"
    if username == "testuser":
        return Usuario(username=username, nombre="Usuario de Prueba")  # Asegúrate de tener una clase Usuario definida
    return None

def crear_access_token(data: dict):#Recibimos un objeto del tipo diccionario que podria ser tambien un JSON
    to_encode = data.copy() #Creamos una copia del diccionario para poder operarlo dentro de la funcion
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #Definimos el tiempo que va a durar la sesion de trabajo del usuario que este loggeado
    to_encode.update({"exp": expire}) #Acá estamos agregando la fecha en la que expira este token de loggeo
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) #En esta linea es donde generamos el token de acceso a la sesion que vamos a crear.
    return encoded_jwt #Aca devolvemos el token 


async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Verifica el token de ID de Firebase
        try:
            decoded_token = auth.verify_id_token(token)
            uid: str = decoded_token['uid']  # Obtén el UID del token decodificado
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError, ValueError) as e:
            print(f"Error al verificar el token de Firebase: {e}")
            raise credentials_exception from e

        # Obtén el usuario de tu base de datos usando el UID
        usuario = obtener_usuario(uid) 
        if usuario is None:
            raise credentials_exception
        return usuario

    except JWTError as e:  # Esta excepción ya no debería ocurrir, pero la dejamos por si acaso
        print(f"Error al decodificar el token JWT: {e}")
        raise credentials_exception from e