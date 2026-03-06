from flask import Blueprint, request, jsonify
import pandas as pd
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from src.utils.db_session import get_db_session
from src.model.laser.task_report import TaskReport
from src.utils.task_report_parse import (
    parse_dt,
    parse_duration_to_seconds,
    parse_size_xy,
    to_int,
    to_float,
    parse_hypcut_rtf_log,
)

task_report_import = Blueprint("task_report_import", __name__)

REQUIRED_COLS = {
    "Task Name",
    "Processing Times",
    "Start Time",
    "Time Consumed",
    "Material",
    "Size(mm )",
    "Thickness( mm)",
    "Parts",
    "Cutting Length(mm)",
    "Perforation",
    "End Time",
    "Cutting Speed(mm/s)",
    "Machine",
}

@task_report_import.route("/maquinaLaser12000W/taskreport/import", methods=["POST"])
def importar_taskreport_excel():
    print("\n[TASKREPORT] ===== HIT importar_taskreport_excel =====", flush=True)
    print("[TASKREPORT] method:", request.method, flush=True)
    print("[TASKREPORT] content-type:", request.content_type, flush=True)
    print("[TASKREPORT] form keys:", list(request.form.keys()), flush=True)
    print("[TASKREPORT] files keys:", list(request.files.keys()), flush=True)

    f = request.files.get("file")
    if not f:
        return jsonify({"status": 1, "msg": "Falta archivo: field 'file'"}), 400

    sheet = request.form.get("sheet", "0")
    mode = (request.form.get("mode") or "upsert").lower()

    try:
        sheet = int(sheet) if sheet.isdigit() else sheet
    except Exception:
        sheet = 0

    try:
        df = pd.read_excel(f, sheet_name=sheet, engine="openpyxl")
        print("[TASKREPORT] columns:", df.columns.tolist(), flush=True)
        rename_map = {
            "Size(mm)": "Size(mm )",
            "Thickness(mm)": "Thickness( mm)",
        }
        df.rename(columns=rename_map, inplace=True)

        missing = sorted(list(REQUIRED_COLS - set(df.columns)))
        print("[TASKREPORT] missing:", missing, flush=True)
        if missing:
            return jsonify({"status": 1, "msg": "Columnas faltantes", "missing": missing}), 400

        print("[TASKREPORT] read_excel OK. shape=", df.shape, flush=True)
    except Exception as e:
        print("[TASKREPORT][read_excel] ERROR:", repr(e), flush=True)
        return jsonify({"status": 1, "msg": f"No pude leer el Excel: {e}"}), 400

    df.columns = [str(c).strip() for c in df.columns]
    missing = sorted(list(REQUIRED_COLS - set(df.columns)))
    if missing:
        return jsonify({"status": 1, "msg": "Columnas faltantes", "missing": missing}), 400

    inserted = 0
    updated = 0
    skipped = 0

    # ✅ evita duplicados dentro del MISMO Excel (mismo key repetido)
    seen_keys = set()

    try:
        with get_db_session() as session:
            for _, row in df.iterrows():
                task_name = str(row.get("Task Name") or "").strip()
                if not task_name:
                    skipped += 1
                    continue

                start_time = parse_dt(row.get("Start Time"))
                end_time = parse_dt(row.get("End Time"))
                machine = str(row.get("Machine") or "").strip() or None

                time_s = parse_duration_to_seconds(row.get("Time Consumed"))
                size_raw, sx, sy = parse_size_xy(row.get("Size(mm )"))

                payload = dict(
                    task_name=task_name,
                    processing_times=to_int(row.get("Processing Times")),
                    start_time=start_time,
                    end_time=end_time,
                    time_consumed_s=time_s,
                    material=str(row.get("Material") or "").strip() or None,
                    size_raw=size_raw,
                    size_x_mm=sx,
                    size_y_mm=sy,
                    thickness_mm=to_float(row.get("Thickness( mm)")),
                    parts=to_int(row.get("Parts")),
                    cutting_length_mm=to_float(row.get("Cutting Length(mm)")),
                    perforation=to_int(row.get("Perforation")),
                    cutting_speed_mms=to_float(row.get("Cutting Speed(mm/s)")),
                    machine=machine,
                )

                # =========================
                # INSERT_ONLY sin duplicados
                # =========================
                if mode == "insert_only":
                    # sin start_time no hay clave confiable para dedupe
                    if start_time is None:
                        skipped += 1
                        continue

                    key = (task_name, start_time, machine)

                    # 1) dedupe dentro del mismo excel
                    if key in seen_keys:
                        skipped += 1
                        continue
                    seen_keys.add(key)

                    # 2) dedupe contra DB
                    exists = (
                        session.query(TaskReport.id)
                        .filter_by(task_name=task_name, start_time=start_time, machine=machine)
                        .first()
                    )
                    if exists:
                        skipped += 1
                        continue

                    session.add(TaskReport(**payload))
                    inserted += 1
                    continue

                # ==========
                # UPSERT (igual que antes)
                # ==========
                existing = None
                if start_time is not None:
                    existing = (
                        session.query(TaskReport)
                        .filter_by(task_name=task_name, start_time=start_time, machine=machine)
                        .first()
                    )

                if existing:
                    for k, v in payload.items():
                        setattr(existing, k, v)
                    updated += 1
                else:
                    session.add(TaskReport(**payload))
                    inserted += 1

        return jsonify({
            "status": 0,
            "msg": "OK",
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped
        }), 200

    except IntegrityError as e:
        return jsonify({"status": 1, "msg": f"IntegrityError: {str(getattr(e, 'orig', e))}"}), 409
    except Exception as e:
        return jsonify({"status": 1, "msg": f"Error importando: {e}"}), 500


@task_report_import.route("/maquinaLaser12000W/taskreport/import_rtf", methods=["POST"])
def importar_taskreport_rtf():
    """Importa cortes desde un log HypCut en formato RTF.

    Espera:
      - file: archivo .rtf subido (field "file")
      - machine (opcional): nombre de la máquina
      - task_name (opcional): prefijo para el nombre de tarea
      - mode (opcional): "upsert" (default) o "insert_only"
    """

    print("\n[TASKREPORT][RTF] ===== HIT importar_taskreport_rtf =====", flush=True)
    print("[TASKREPORT][RTF] form keys:", list(request.form.keys()), flush=True)
    print("[TASKREPORT][RTF] files keys:", list(request.files.keys()), flush=True)

    f = request.files.get("file")
    if not f:
        return jsonify({"status": 1, "msg": "Falta archivo: field 'file'"}), 400

    mode = (request.form.get("mode") or "upsert").lower()
    machine = (request.form.get("machine") or "").strip() or None
    task_name_prefix = (request.form.get("task_name") or "HypCut").strip() or "HypCut"

    try:
        raw_text = f.read().decode("utf-8", errors="ignore")
    except Exception:
        # si ya es str (por ejemplo en tests), usar tal cual
        raw_text = f.read() if isinstance(f.read(), str) else ""

    # parseo básico usando los helpers de utils
    jobs = parse_hypcut_rtf_log(raw_text)
    if not jobs:
        return jsonify({"status": 1, "msg": "No se encontraron cortes en el log RTF"}), 400

    inserted = 0
    updated = 0
    skipped = 0

    seen_keys = set()
    current_year = datetime.utcnow().year

    try:
        with get_db_session() as session:
            for idx, job in enumerate(jobs, start=1):
                # start viene como "MM/DD HH:MM:SS" (sin año)
                start_str = job.get("start")
                start_dt = None
                if start_str:
                    try:
                        month = int(start_str[0:2])
                        day = int(start_str[3:5])
                        time_part = start_str[6:]
                        hh, mm, ss = map(int, time_part.split(":"))
                        start_dt = datetime(current_year, month, day, hh, mm, ss)
                    except Exception:
                        start_dt = None

                duration_s = job.get("time_consumed_s") or None
                end_dt = None
                if start_dt is not None and duration_s is not None:
                    try:
                        end_dt = start_dt + timedelta(seconds=float(duration_s))
                    except Exception:
                        end_dt = None

                task_name = f"{task_name_prefix}_{idx}"

                payload = dict(
                    task_name=task_name,
                    processing_times=None,
                    start_time=start_dt,
                    end_time=end_dt,
                    time_consumed_s=duration_s,
                    material=None,
                    size_raw=None,
                    size_x_mm=None,
                    size_y_mm=None,
                    thickness_mm=None,
                    parts=None,
                    cutting_length_mm=job.get("cutting_length_mm"),
                    perforation=job.get("perforation"),
                    cutting_speed_mms=None,
                    machine=machine,
                )

                # dedupe en modo insert_only, igual que el Excel
                if mode == "insert_only":
                    if start_dt is None:
                        skipped += 1
                        continue

                    key = (task_name, start_dt, machine)

                    if key in seen_keys:
                        skipped += 1
                        continue
                    seen_keys.add(key)

                    exists = (
                        session.query(TaskReport.id)
                        .filter_by(task_name=task_name, start_time=start_dt, machine=machine)
                        .first()
                    )
                    if exists:
                        skipped += 1
                        continue

                    session.add(TaskReport(**payload))
                    inserted += 1
                    continue

                # modo upsert (default)
                existing = None
                if start_dt is not None:
                    existing = (
                        session.query(TaskReport)
                        .filter_by(task_name=task_name, start_time=start_dt, machine=machine)
                        .first()
                    )

                if existing:
                    for k, v in payload.items():
                        setattr(existing, k, v)
                    updated += 1
                else:
                    session.add(TaskReport(**payload))
                    inserted += 1

        return jsonify(
            {
                "status": 0,
                "msg": "OK",
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped,
            }
        ), 200

    except IntegrityError as e:
        return jsonify({"status": 1, "msg": f"IntegrityError: {str(getattr(e, 'orig', e))}"}), 409
    except Exception as e:
        return jsonify({"status": 1, "msg": f"Error importando RTF: {e}"}), 500
