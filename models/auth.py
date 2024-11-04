from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth, firestore
from pydantic import BaseModel

# Configurando las claves básicas para manipular el acceso a la data.
SECRET_KEY = "pruebatecnica"  # Reemplaza con una clave secreta fuerte
ALGORITHM = "HS256"  # Algoritmo de encriptación que vamos a usar para la API
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tiempo en el que vence la sesión de trabajo.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Usaremos esto más adelante

class Usuario(BaseModel):
    username: str
    nombre: str


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
            uid: str = decoded_token['uid']
            email: str = decoded_token['email']  # Obtén el email del token
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError, ValueError) as e:
            print(f"Error al verificar el token de Firebase: {e}")
            raise credentials_exception from e

        # Crea un objeto Usuario con la información del token
        usuario = Usuario(username=uid, nombre=email)  # Usa el email como nombre

        return usuario

    except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError, ValueError) as e:
        print(f"Error al verificar el token de Firebase: {e}")
        # Puedes personalizar el mensaje de error según el tipo de excepción
        if isinstance(e, auth.InvalidIdTokenError):
            raise HTTPException(status_code=401, detail="Token de Firebase inválido") from e
        elif isinstance(e, auth.ExpiredIdTokenError):
            raise HTTPException(status_code=401, detail="Token de Firebase expirado") from e
        # ... (manejo de otras excepciones) ...
        raise credentials_exception from e