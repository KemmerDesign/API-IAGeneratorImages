from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


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

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    #Acá manejamos excepcion de usuario por enede token no autorizado
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        #acá validamos que el usuario no este vacio
        if username is None:
            raise credentials_exception
        #Al llegar aca se demostro que el username que esta llegando no esta vacio asi que 
        #procede a buscar el usuario con el metodo que asignamos
        usuario = obtener_usuario(username)
        #Si el usuario no fue encontrado y esta vacio lanza la excepcion
        if usuario is None:
            raise credentials_exception
        #acá devuelve el usuario por que fue encontrado.
        return usuario
    except JWTError:
        raise credentials_exception