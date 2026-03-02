import requests
from bs4 import BeautifulSoup
import pdfplumber
import os
import re
import time
import urllib3
import shutil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

estudiantes_ids = [
    "0332141012",
    "0332161012",
    "0332222001",
    "0332222002",
    "0332222003",
    "0332222004",
    "0332222005",
    "0332222006",
    "0332222007",
    "0332222008",
    "0332222009",
    "0332222010",
    "0332222011",
    "0332222012",
    "0332222013",
    "0332222014",
    "0332222015",
    "0332222016",
    "0332222017",
    "0332222018",
    "0332222019",
    "0332222020",
    "0332222021",
    "0332222022",
    "0332222023",
    "0332222024",
    "0332222025",
    "0332222026",
    "0332222027",
    "0332222028",
    "0332222029",
    "0332222030",
    "0332222031",
    "0332222032",
    "0332222033",
    "0332222034",
    "0332231042",
    "0332231013",
    "0332231002"
]

URL = "https://intranet.unjfsc.edu.pe/Docentes/HorarioPorCodigoUniversitario.aspx"
FOLDER_PDFS = "pdfs_temp"
HTML_NAME = "index.html"

if not os.path.exists(FOLDER_PDFS): os.makedirs(FOLDER_PDFS)

def limpiar_curso(n):
    n = str(n).upper().strip()
    basura_regex = r'[- ]+(TEOR[IÍ]A|PR[AÁ]CTICA|[A-Z]|\d+)$'
    
    # "-A-PRÁCTICA-2"
    while True:
        nuevo_n = re.sub(basura_regex, '', n).strip()
        if nuevo_n == n:
            break
        n = nuevo_n
    
    # Caso especial: (INVESTIGACIÓNPRÁCTICA)
    n = re.sub(r'(TEOR[IÍ]A|PR[AÁ]CTICA)$', '', n).strip()
    
    return n

def descargar_pdf(sid):
    print(f"Descargando {sid}...")
    s = requests.Session()
    h = {"User-Agent": "Mozilla/5.0", "Referer": URL}
    try:
        r1 = s.get(URL, headers=h, verify=False, timeout=20)
        soup = BeautifulSoup(r1.text, 'html.parser')
        tokens = {t['name']: t.get('value', '') for t in soup.find_all('input', type='hidden')}
        tokens.update({"ctl00$ContentPlaceHolder1$txtcodigouniversitario": sid, "ctl00$ContentPlaceHolder1$btnaceptar": "ACEPTAR"})
        r2 = s.post(URL, data=tokens, headers=h, verify=False)
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        tokens2 = {t['name']: t.get('value', '') for t in soup2.find_all('input', type='hidden')}
        tokens2.update({"ctl00$ContentPlaceHolder1$txtcodigouniversitario": sid, "ctl00$ContentPlaceHolder1$btnPDF.x": "10", "ctl00$ContentPlaceHolder1$btnPDF.y": "10"})
        r3 = s.post(URL, data=tokens2, headers=h, verify=False)
        if r3.status_code == 200 and b'%PDF' in r3.content:
            with open(os.path.join(FOLDER_PDFS, f"{sid}.pdf"), "wb") as f: f.write(r3.content)
            return True
    except: pass
    return False

def extraer_data(path):
    with pdfplumber.open(path) as pdf:
        txt = pdf.pages[0].extract_text()
        nom = re.search(r"APELLIDOS Y NOMBRES\s*:\s*(.*?)\s+PLAN", txt).group(1).strip()
        cod = re.search(r"CÓDIGO UNIVERSITARIO\s*:\s*(\d+)", txt).group(1)

        lista_final = []
        for page in pdf.pages:
            table = page.extract_table({"vertical_strategy": "lines", "horizontal_strategy": "lines"})
            if table:
                acum = ""
                for row in table:
                    if not row or not row[0]: continue
                    c, h = str(row[0]).replace('\n', ' ').strip(), row[1]
                    if c and "CURSO" not in c and "H O R A R I O" not in c:
                        if not h: acum += " " + c
                        else: 
                            raw_name = (acum + " " + c).upper()
                            clean_name = limpiar_curso(raw_name)
                            
                            if "TEOR" in raw_name:
                                lista_final.append(clean_name)
                            elif "PRAC" in raw_name or "PRÁC" in raw_name:
                                if clean_name not in lista_final:
                                    lista_final.append(clean_name)
                            
                            acum = ""

        return {"nom": nom, "cod": cod, "cursos": sorted(lista_final)}

def generar_html(data):
    total = len(data)
    matriculados = sum(1 for e in data if e['cursos'])
    
    rows = ""
    for e in data:
        estado = "SI" if e['cursos'] else "NO"
        color_estado = "color: green;" if e['cursos'] else "color: red;"
        lista_cursos = "<ul>" + "".join([f"<li>{c}</li>" for c in e['cursos']]) + "</ul>" if e['cursos'] else "-"
        
        rows += f"""
        <tr>
            <td>{e['cod']}</td>
            <td><b>{e['nom'].upper()}</b></td>
            <td style="text-align:center; font-weight:bold; {color_estado}">{estado}</td>
            <td class="cursos">{lista_cursos}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Matrícula</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f8f8f8; padding: 20px; }}
        .container {{ max-width: 1300px; margin: auto; }}
        .header {{ border-bottom: 2px solid #333; margin-bottom: 20px; padding-bottom: 10px; }}
        h2 {{ margin: 0; text-transform: uppercase; }}
        .info {{ font-size: 14px; margin-top: 5px; }}
        .table-container {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; min-width: 600px; }}
        th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
        th {{ background-color: #f4f4f4; font-size: 12px; text-transform: uppercase; }}
        td {{ background-color: #ffffff; font-size: 13px; vertical-align: top; }}
        .cursos ul {{ margin: 0; padding-left: 15px; font-size: 11px; }}
        @media (max-width: 600px) {{
            body {{ padding: 10px; }}
            h2 {{ font-size: 18px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Reporte de Matrícula</h2>
            <div class="info">
                Actualizado: {time.strftime('%d/%m/%Y %H:%M')}<br>
                Total: {total} | Matriculados: {matriculados}
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 100px;">Código</th>
                        <th>Nombre del Estudiante</th>
                        <th style="width: 50px;">Matrícula</th>
                        <th>Cursos</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    with open(HTML_NAME, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    for sid in estudiantes_ids:
        descargar_pdf(sid)
        time.sleep(0.5)

    final_data = []
    for sid in estudiantes_ids:
        path = os.path.join(FOLDER_PDFS, f"{sid}.pdf")
        if os.path.exists(path):
            d = extraer_data(path)
            if d: final_data.append(d)
        else:
            final_data.append({"nom": "No encontrado", "cod": sid, "cursos": []})

    if final_data:
        final_data.sort(key=lambda x: x['nom'])
        generar_html(final_data)
        print("Reporte index.html generado.")

    if os.path.exists(FOLDER_PDFS):
        shutil.rmtree(FOLDER_PDFS)