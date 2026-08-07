import re
import logging
from typing import Optional
import pdfplumber

from .models import StudentRecord

logger = logging.getLogger(__name__)

def limpiar_curso(n: str) -> str:
    n = str(n).upper().strip()
    basura_regex = r'[- ]+(TEOR[IÍ]A|PR[AÁ]CTICA|[A-Z]|\d+)$'
    while True:
        nuevo_n = re.sub(basura_regex, '', n).strip()
        if nuevo_n == n:
            break
        n = nuevo_n
    n = re.sub(r'(TEOR[IÍ]A|PR[AÁ]CTICA)$', '', n).strip()
    return n

def extraer_data(path: str, grupo_nombre: str) -> Optional[StudentRecord]:
    try:
        with pdfplumber.open(path) as pdf:
            txt = pdf.pages[0].extract_text()
            if not txt:
                return None
                
            nom_match = re.search(r"APELLIDOS Y NOMBRES\s*:\s*(.*?)\s+PLAN", txt)
            cod_match = re.search(r"CÓDIGO UNIVERSITARIO\s*:\s*(\d+)", txt)
            
            if not nom_match or not cod_match:
                return None
                
            nom = nom_match.group(1).strip()
            cod = cod_match.group(1).strip()
            
            lista_final = []
            for page in pdf.pages:
                table = page.extract_table({"vertical_strategy": "lines", "horizontal_strategy": "lines"})
                if table:
                    acum = ""
                    for row in table:
                        if not row or not row[0]:
                            continue
                        c = str(row[0]).replace('\n', ' ').strip()
                        h = row[1]
                        if c and "CURSO" not in c and "H O R A R I O" not in c:
                            if not h:
                                acum += " " + c
                            else:
                                raw_name = (acum + " " + c).upper()
                                clean_name = limpiar_curso(raw_name)

                                if "TEOR" in raw_name:
                                    lista_final.append(clean_name)
                                elif "PRAC" in raw_name or "PRÁC" in raw_name:
                                    if clean_name not in lista_final:
                                        lista_final.append(clean_name)
                                acum = ""
            return StudentRecord(nom=nom, cod=cod, cursos=sorted(lista_final), grupo=grupo_nombre)
    except Exception as e:
        logger.error(e)
        return None
