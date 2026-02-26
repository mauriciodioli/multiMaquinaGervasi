from utils.db import db
from flask import Blueprint
from flask_marshmallow import Marshmallow

from sqlalchemy import UniqueConstraint

ma = Marshmallow()

task_report = Blueprint('task_report', __name__)

class TaskReport(db.Model):
    __tablename__ = "task_report"
    __table_args__ = (
        UniqueConstraint("task_name", "start_time", "machine", name="uq_task_start_machine"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)

    task_name = db.Column(db.String(512), nullable=False)
    processing_times = db.Column(db.Integer, nullable=True)

    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)

    time_consumed_s = db.Column(db.Float, nullable=True)

    material = db.Column(db.String(255), nullable=True)

    size_raw = db.Column(db.String(64), nullable=True)   # "904X570"
    size_x_mm = db.Column(db.Integer, nullable=True)
    size_y_mm = db.Column(db.Integer, nullable=True)

    thickness_mm = db.Column(db.Float, nullable=True)

    parts = db.Column(db.Integer, nullable=True)
    cutting_length_mm = db.Column(db.Float, nullable=True)
    perforation = db.Column(db.Integer, nullable=True)

    cutting_speed_mms = db.Column(db.Float, nullable=True)
    machine = db.Column(db.String(128), nullable=True)


class TaskReportSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "task_name",
            "processing_times",
            "start_time",
            "end_time",
            "time_consumed_s",
            "material",
            "size_raw",
            "size_x_mm",
            "size_y_mm",
            "thickness_mm",
            "parts",
            "cutting_length_mm",
            "perforation",
            "cutting_speed_mms",
            "machine",
        )
