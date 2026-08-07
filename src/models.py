import time
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

@dataclass
class StudentRecord:
    nom: str
    cod: str
    cursos: List[str]
    grupo: str

def actualizar_historial(old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]], historial_actual: Dict[str, List[Dict[str, str]]]) -> Tuple[List[str], Dict[str, List[Dict[str, str]]]]:

    novedades_globales = []
    fecha_actual = time.strftime('%d/%m/%Y %H:%M')
    
    if not old_data:
        novedades_globales.append("Es la primera vez que se ejecuta el sistema. No hay base anterior para comparar.")
        return novedades_globales, historial_actual

    old_dict = {item['cod']: item for item in old_data if item['nom'] != 'No encontrado'}
    
    for item in new_data:
        if item['nom'] == 'No encontrado':
            continue
            
        cod = item['cod']
        nom = item['nom'].title()
        cursos_nuevos = set(item['cursos'])
        

        if cod not in historial_actual:
            historial_actual[cod] = []
            
        agregados_lista = []
        retirados_lista = []
        
        if cod not in old_dict:
            agregados_lista = list(cursos_nuevos)
            novedades_globales.append(f"<b>{nom}</b> aparecio en el sistema por primera vez.")
        else:
            cursos_viejos = set(old_dict[cod]['cursos'])
            agregados = cursos_nuevos - cursos_viejos
            retirados = cursos_viejos - cursos_nuevos
            
            agregados_lista = list(agregados)
            retirados_lista = list(retirados)
            
            for c in agregados:
                novedades_globales.append(f"<b>{nom}</b> se matriculo en: {c}")
                
            for c in retirados:
                novedades_globales.append(f"<b>{nom}</b> se retiro de: {c}")
                

        if agregados_lista or retirados_lista:
            historial_actual[cod].append({
                "fecha": fecha_actual,
                "agregados": agregados_lista,
                "retirados": retirados_lista
            })
                
    if not novedades_globales:
        novedades_globales.append("No se detectaron cambios desde la ultima revision.")
        
    return novedades_globales, historial_actual
