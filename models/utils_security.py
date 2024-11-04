from fastapi.security import OAuth2PasswordBearer
from controllers.controllers import db, firebase_app
from models.auth import Usuario



async def obtener_usuario(username: str):
    try:
        # Obtener el usuario de Firestore usando el UID (username)
        user_doc = db.collection('usuarios').document(username).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return Usuario(username=username, nombre=user_data.get('nombre', 'Desconocido'))
        else:
            return None
    except Exception as e:
        print(f"Error al obtener el usuario: {e}")
        return None