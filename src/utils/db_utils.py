# utils/db_utils.py
def crear_tablas(app, db):
    with app.app_context():
        db.create_all()
        print("✅ Tablas creadas correctamente")
       
