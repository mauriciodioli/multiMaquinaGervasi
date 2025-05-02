from flask import Blueprint, render_template, request, redirect, url_for,jsonify
from src.model.maquina import Maquina
from utils.db import db
from datetime import datetime
import json

crud_front_end_maquinas = Blueprint('crud_front_end_maquinas', __name__)



