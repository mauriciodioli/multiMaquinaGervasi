from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import hashlib
import time
import os
import requests

from src.model.maquina import Maquina
from src.model.usuario import Usuario
from src.utils.db import db
from src.utils.get_textos_menu import get_textos_menu
from src.utils.db_session import get_db_session

conexionAPI = Blueprint("conexionAPI", __name__)

# ==========================
# CONFIG BOCHU
# ==========================

# Idealmente los cargás por variables de entorno o desde config.py
BOCHU_APP_ID = os.getenv("BOCHU_APP_ID")        # ej: "op18fae9053154d49"
BOCHU_APP_SECRET = os.getenv("BOCHU_APP_SECRET")  # ej: "1e02e5f10c2f4bcd..."
BOCHU_BASE_URL = os.getenv("BOCHU_BASE_URL") or "https://mcs-gateway.fscut.com"
BOCHU_ORG_CODE = os.getenv("BOCHU_ORG_CODE")    # ej: "TU_ORGCODE"
ID_CARD_ID = "241111132743"  # reemplazá con el cardId de tu máquina para pruebas

DEBUG_BOCHU = True

# ==========================
# HELPERS
# ==========================

def _build_bochu_headers():
    if not BOCHU_APP_ID or not BOCHU_APP_SECRET:
        raise RuntimeError("Falta BOCHU_APP_ID / BOCHU_APP_SECRET")

    timestamp = str(int(time.time() * 1000))
    raw = f"{BOCHU_APP_ID}{BOCHU_APP_SECRET}{timestamp}"
    app_sign = hashlib.md5(raw.encode("utf-8")).hexdigest()

    return {
        "app-id": BOCHU_APP_ID,
        "time-stamp": timestamp,
        "app-sign": app_sign,
        "Content-Type": "application/json",
    }





# ==========================
# RUTAS
# ==========================
@conexionAPI.route("/bochu/machines", methods=["GET"])
def bochu_machines():
    headers = _build_bochu_headers()
    url = f"{BOCHU_BASE_URL}/api/user_devices"

    resp = requests.post(url, json={}, headers=headers, timeout=15)
    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text}

    return jsonify(data), resp.status_code

@conexionAPI.route("/bochu/test", methods=["GET"])
def test_bochu_conexion():
    card_id = request.args.get("cardId") or ID_CARD_ID

    headers = _build_bochu_headers()
    url = f"{BOCHU_BASE_URL}/api/user_devices/current_state"
    payload = {"cardIds": [card_id]}

    resp = requests.post(url, json=payload, headers=headers, timeout=10)

    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text}

    # Bochu puede devolver lista o dict según endpoint: aceptamos ambos
    return jsonify({
        "ok": resp.ok,                 # True si 200-299
        "status_code": resp.status_code,
        "data": data
    }), resp.status_code

@conexionAPI.route("/laser/tasks/completed", methods=["POST"])
def completed_laser_tasks():
    body = request.get_json(silent=True) or {}

    card_id = body.get("cardId") or ID_CARD_ID
    start   = body.get("startTime")
    end     = body.get("endTime")

    if not start or not end:
        return jsonify({
            "ok": False,
            "error": "startTime y endTime son obligatorios"
        }), 400

    headers = _build_bochu_headers()

    url = f"{BOCHU_BASE_URL}/api/production/queryCompletedTaskList"

    payload = {
        "cardId": card_id,
        "startTime": start,
        "endTime": end
    }

    try:
       
        t0 = time.time()
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        elapsed = round(time.time() - t0, 3)
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": f"Bochu connection error: {e}"
        }), 502

    try:
        raw = resp.json()
    except ValueError:
        return jsonify({
            "ok": False,
            "error": "Invalid JSON from Bochu",
            "raw": resp.text
        }), resp.status_code

    # 🔥 CASO CLAVE: PERMISO NO HABILITADO
    if raw.get("status") == 1007:
        return jsonify({
            "ok": False,
            "blocked": True,
            "code": 1007,
            "error": "Bochu API permission denied: production history not enabled",
            "hint": "Contact Bochu to enable 'Query completed task list for the machine tool'"
        }), 403

    if not resp.ok or raw.get("status") != 0:
        return jsonify({
            "ok": False,
            "error": raw.get("msg", "Unknown Bochu error"),
            "raw": raw
        }), 502

    tasks = raw.get("data", [])

    return jsonify({
        "ok": True,
        "cardId": card_id,
        "count": len(tasks),
        "tasks": tasks,
        "response_time_sec": elapsed

    })


def normalize_tasks(raw):
    out = []
    for t in raw.get("data", []):
        out.append({
            "job_name": t.get("taskName"),
            "material": t.get("materialName"),
            "thickness_mm": t.get("thickness"),
            "dimensions": t.get("size"),
            "pieces": t.get("pieceQty"),
            "cut_length_mm": t.get("cutLength"),
            "speed_mm_s": t.get("cutSpeed"),
            "start_time": t.get("startTime"),
            "end_time": t.get("endTime"),
            "duration_sec": t.get("workTime")
        })
    return out

@conexionAPI.route("/laser/jobs/list", methods=["POST"])
def jobs_list_test():
    headers = _build_bochu_headers()
    url = f"{BOCHU_BASE_URL}/api/job/list"

    resp = requests.post(url, json={}, headers=headers, timeout=10)
    raw = resp.json()

    return jsonify({
        "ok": resp.ok,
        "status": raw.get("status"),
        "msg": raw.get("msg")
    })


def normalize_dt(v):
    # "2026-01-30T09:58" → "2026-01-30 09:58:00"
    return datetime.fromisoformat(v).strftime("%Y-%m-%d %H:%M:%S")