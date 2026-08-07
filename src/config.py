import os
import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class Config:
    URL = "https://intranet.unjfsc.edu.pe/Docentes/HorarioPorCodigoUniversitario.aspx"
    FOLDER_PDFS = "pdfs_temp"
    HTML_NAME = "index.html"
    ESTADO_FILE = "data/estado_anterior.json"
    HISTORIAL_FILE = "data/historial.json"
    CONFIG_FILE = "data/config.json"
    CURSOS_FILE = "data/cursos.json"
    MAX_THREADS = 5

def cargar_creditos(config: Config) -> Dict[str, int]:
    if not os.path.exists(config.CURSOS_FILE):
        return {}
    try:
        with open(config.CURSOS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {c[0].upper().strip(): int(c[1]) for c in data}
    except Exception as e:
        logger.error(e)
        return {}

def cargar_grupos(config: Config) -> Dict[str, List[str]]:
    if not os.path.exists(config.CONFIG_FILE):
        return {}
    try:
        with open(config.CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("grupos_estudiantes", {})
    except Exception as e:
        logger.error(e)
        return {}
