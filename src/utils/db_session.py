# src/utils/db_session.py
from contextlib import contextmanager
from utils.db import db

@contextmanager
def get_db_session():
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise
    finally:
        db.session.close()
