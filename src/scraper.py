import os
import logging
import requests
from bs4 import BeautifulSoup

from .config import Config

logger = logging.getLogger(__name__)

def descargar_pdf(sid: str, config: Config) -> bool:
    path = os.path.join(config.FOLDER_PDFS, f"{sid}.pdf")
    if os.path.exists(path):
        return True
        
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0", "Referer": config.URL}
    
    try:
        r1 = session.get(config.URL, headers=headers, verify=False, timeout=20)
        soup = BeautifulSoup(r1.text, 'html.parser')
        tokens = {t['name']: t.get('value', '') for t in soup.find_all('input', type='hidden')}
        tokens.update({
            "ctl00$ContentPlaceHolder1$txtcodigouniversitario": sid,
            "ctl00$ContentPlaceHolder1$btnaceptar": "ACEPTAR"
        })
        
        r2 = session.post(config.URL, data=tokens, headers=headers, verify=False, timeout=20)
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        tokens2 = {t['name']: t.get('value', '') for t in soup2.find_all('input', type='hidden')}
        tokens2.update({
            "ctl00$ContentPlaceHolder1$txtcodigouniversitario": sid,
            "ctl00$ContentPlaceHolder1$btnPDF.x": "10",
            "ctl00$ContentPlaceHolder1$btnPDF.y": "10"
        })
        
        r3 = session.post(config.URL, data=tokens2, headers=headers, verify=False, timeout=20)
        if r3.status_code == 200 and b'%PDF' in r3.content:
            with open(path, "wb") as f:
                f.write(r3.content)
            print(f"Descargado PDF: {sid}")
            return True
    except requests.exceptions.RequestException as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
        
    return False
