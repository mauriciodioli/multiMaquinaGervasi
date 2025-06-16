from flask import request
from src.model.usuario import Usuario  # ajustá el import según tu estructura
from src import db

def current_user():
    try:
        user_id = request.cookies.get("user_id")
        if user_id:
            return db.session.get(Usuario, int(user_id))
    except:
        return None
