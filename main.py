import os
import json
import shutil
import logging
import concurrent.futures
from dataclasses import asdict
import urllib3

from src.config import Config, cargar_creditos, cargar_grupos
from src.scraper import descargar_pdf
from src.parser import extraer_data
from src.models import actualizar_historial
from src.html_generator import generar_html

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def main():
    config = Config()
    dict_creditos = cargar_creditos(config)
    grupos_estudiantes = cargar_grupos(config)
    
    if not grupos_estudiantes:
        return

    if not os.path.exists(config.FOLDER_PDFS):
        os.makedirs(config.FOLDER_PDFS)

    todos_los_ids = set()
    for lista in grupos_estudiantes.values():
        todos_los_ids.update(lista)

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_THREADS) as executor:
        list(executor.map(lambda sid: descargar_pdf(sid, config), todos_los_ids))

    final_data = []
    for nombre_grupo, lista_ids in grupos_estudiantes.items():
        for sid in lista_ids:
            path = os.path.join(config.FOLDER_PDFS, f"{sid}.pdf")
            if os.path.exists(path):
                record = extraer_data(path, nombre_grupo)
                if record:
                    final_data.append(asdict(record))
            else:
                final_data.append({
                    "nom": "No encontrado",
                    "cod": sid,
                    "cursos": [],
                    "grupo": nombre_grupo
                })

    if final_data:
        final_data.sort(key=lambda x: x['nom'])
        
        old_data = []
        if os.path.exists(config.ESTADO_FILE):
            try:
                with open(config.ESTADO_FILE, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
            except Exception as e:
                pass
                
        historial = {}
        if os.path.exists(config.HISTORIAL_FILE):
            try:
                with open(config.HISTORIAL_FILE, "r", encoding="utf-8") as f:
                    historial = json.load(f)
            except Exception as e:
                pass
                
        novedades, historial = actualizar_historial(old_data, final_data, historial)
        generar_html(final_data, dict_creditos, config, novedades, historial)
        
        with open(config.ESTADO_FILE, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
        with open(config.HISTORIAL_FILE, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=4)

    if os.path.exists(config.FOLDER_PDFS):
        shutil.rmtree(config.FOLDER_PDFS)

if __name__ == "__main__":
    main()