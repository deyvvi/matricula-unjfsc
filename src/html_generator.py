import time
import json
from typing import Dict, List, Any, Optional
from .config import Config

def generar_html(data: List[Dict[str, Any]], dict_creditos: Dict[str, int], config: Config, novedades: Optional[List[str]] = None, historial: Optional[Dict[str, Any]] = None) -> None:
    novedades = novedades or []
    historial = historial or {}
    total = len(data)
    matriculados = sum(1 for e in data if e['cursos'])
    grupos_unicos = sorted(list(set(e['grupo'] for e in data)))

    tab_buttons = "<button class='tab active' onclick='filtrar(this, \"todos\")'>TODOS</button>"
    for g in grupos_unicos:
        tab_buttons += "<button class='tab' onclick='filtrar(this, \"" + g + "\")'>" + g.upper() + "</button>"

    rows = ""
    for e in data:
        estado_html = "<span style='color: green; font-weight:bold;'>SI</span>" if e['cursos'] else "<span style='color: red; font-weight:bold;'>NO</span>"
        suma_total_creditos = 0
        lista_li = []

        for curso_nombre in e['cursos']:
            cr = dict_creditos.get(curso_nombre, 0)
            suma_total_creditos += cr
            lista_li.append("<li>" + curso_nombre + " <span style='color:#333; font-size:11px;'>(" + str(cr) + ")</span></li>")

        lista_cursos_html = "<ul>" + "".join(lista_li) + "</ul>" if e['cursos'] else "-"
        
        historial_estudiante = historial.get(e['cod'], [])
        boton_historial = ""
        if historial_estudiante:
            boton_historial = "<button style='float:right; border:1px solid #333; background:#eee; padding:2px 5px; font-size:10px; cursor:pointer;' onclick='verHistorialEstudiante(\"" + e["cod"] + "\", \"" + e["nom"] + "\")'>Ver Historial</button>"
        
        rows += '<tr class="fila-estudiante" data-grupo="' + e['grupo'] + '">'
        rows += '<td>' + e['cod'] + '</td>'
        rows += '<td><b>' + e['nom'] + '</b>' + boton_historial + '</td>'
        rows += '<td style="text-align:center;">' + estado_html + '</td>'
        rows += '<td class="cursos">' + lista_cursos_html + '</td>'
        rows += '<td style="text-align:center; font-weight:bold;">' + (str(suma_total_creditos) if suma_total_creditos > 0 else "-") + '</td>'
        rows += '</tr>'

    if not novedades:
        novedades_html = "<li>No se detectaron movimientos recientes.</li>"
    else:
        novedades_html = "".join(["<li>" + nov + "</li>" for nov in novedades])

    historial_json = json.dumps(historial)
    tiempo_actual = time.strftime('%d/%m/%Y %H:%M')

    html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Matrícula</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f8f8f8; padding: 20px; }
        .container { max-width: 1300px; margin: auto; }
        .header { border-bottom: 1px solid #ccc; margin-bottom: 20px; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: flex-end; }
        h2 { margin: 0; text-transform: uppercase; }
        .info { font-size: 14px; margin-top: 5px; color: #555; }
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; min-width: 600px; }
        th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
        th { background-color: #f4f4f4; font-size: 12px; text-transform: uppercase; }
        td { background-color: #ffffff; font-size: 13px; vertical-align: top; }
        .cursos ul { margin: 0; padding-left: 15px; font-size: 11px; }

        .tabs-container { display: flex; gap: 15px; margin-bottom: 0px; border-bottom: 1px solid #ccc; flex-wrap: wrap; }
        .tab { 
            padding: 10px 5px; cursor: pointer; border: none; background: none;
            font-size: 13px; font-weight: bold; color: #888; text-transform: uppercase;
            outline: none; position: relative; transition: 0.2s;
        }
        .tab:hover { color: #333; }
        .tab.active { color: #000; }
        .tab.active::after {
            content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 3px; background: #333;
        }

        .btn-novedades { background: #333; color: white; border: none; padding: 8px 15px; cursor: pointer; font-size: 13px; text-transform: uppercase; border-radius: 4px; }
        .btn-novedades:hover { background: #000; }

        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }
        .modal-content { background: #fff; width: 90%; max-width: 500px; margin: 100px auto; padding: 20px; border: 1px solid #ccc; position: relative; max-height: 80vh; overflow-y: auto; }
        .close-btn { position: absolute; top: 10px; right: 15px; cursor: pointer; font-size: 20px; font-weight: bold; color: #333; }

        @media (max-width: 600px) {
            body { padding: 10px; }
            .container { padding: 10px; }
            .header { flex-direction: column; align-items: flex-start; gap: 10px; }
            h2 { font-size: 18px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h2>Reporte de Matrícula</h2>
                <div class="info">
                    Actualizado: {time}<br>
                    Total: {total} | Matriculados: {matriculados}
                </div>
            </div>
            <button class="btn-novedades" onclick="document.getElementById('modalNovedades').style.display='block'">Últimos Cambios</button>
        </div>

        <div class="tabs-container">
            {tab_buttons}
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 100px;">Código</th>
                        <th>Nombre del Estudiante</th>
                        <th style="width: 50px; text-align:center;">Matrícula</th>
                        <th>Cursos</th>
                        <th style="width: 50px; text-align:center;">Créditos</th>
                    </tr>
                </thead>
                <tbody id="tablaBody">
                    {rows}
                </tbody>
            </table>
        </div>
    </div>


    <div class="modal-overlay" id="modalNovedades">
        <div class="modal-content">
            <span class="close-btn" onclick="document.getElementById('modalNovedades').style.display='none'">&times;</span>
            <h3 style="margin-top:0; border-bottom: 1px solid #ccc; padding-bottom:10px;">Últimos Cambios (General)</h3>
            <ul style="padding-left: 20px; font-size: 13px; line-height: 1.6;">
                {novedades_html}
            </ul>
        </div>
    </div>


    <div class="modal-overlay" id="modalEstudiante">
        <div class="modal-content">
            <span class="close-btn" onclick="document.getElementById('modalEstudiante').style.display='none'">&times;</span>
            <h3 style="margin-top:0; border-bottom: 1px solid #ccc; padding-bottom:10px; font-size:16px;" id="tituloEstudiante">Historial</h3>
            <div id="listaHistorial">
            </div>
        </div>
    </div>

    <script>
        var historialData = {historial_json};

        function verHistorialEstudiante(cod, nom) {
            document.getElementById('tituloEstudiante').innerHTML = "Historial: " + nom;
            var container = document.getElementById('listaHistorial');
            container.innerHTML = "";
            var registros = historialData[cod] || [];
            
            if (registros.length === 0) {
                container.innerHTML = "<div style='padding:10px;'>No hay movimientos en el historial.</div>";
            } else {
                for(var i=0; i<registros.length; i++) {
                    var html = "<div style='border: 1px solid #ccc; margin-bottom: 10px; font-family: Consolas, monospace;'>";
                    html += "<div style='background-color: #e0e0e0; border-bottom: 1px solid #ccc; padding: 8px 10px; font-size: 12px; color: #333;'>";
                    html += "<b>Fecha:</b> " + registros[i].fecha;
                    html += "</div>";
                    html += "<div style='padding: 5px 0; font-size: 12px;'>";
                    
                    var agregados = registros[i].agregados || [];
                    var retirados = registros[i].retirados || [];
                    
                    for(var j=0; j<agregados.length; j++) {
                        html += "<div style='background-color: #e6ffed; padding: 3px 10px; color: #22863a;'>+ " + agregados[j] + "</div>";
                    }
                    for(var k=0; k<retirados.length; k++) {
                        html += "<div style='background-color: #ffeef0; padding: 3px 10px; color: #cb2431;'>- " + retirados[k] + "</div>";
                    }
                    if (agregados.length === 0 && retirados.length === 0) {
                        html += "<div style='padding: 3px 10px; color: #666;'>Sin cambios de cursos.</div>";
                    }
                    
                    html += "</div></div>";
                    container.innerHTML += html;
                }
            }
            document.getElementById('modalEstudiante').style.display = 'block';
        }

        function filtrar(btn, grupo) {
            var tabs = document.getElementsByClassName('tab');
            for(var i=0; i<tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            btn.classList.add('active');

            var filas = document.getElementsByClassName('fila-estudiante');
            for (var i = 0; i < filas.length; i++) {
                var fila = filas[i];
                if (grupo === 'todos' || fila.getAttribute('data-grupo') === grupo) {
                    fila.style.display = '';
                } else {
                    fila.style.display = 'none';
                }
            }
        }

        window.onclick = function(event) {
            var modalNov = document.getElementById('modalNovedades');
            var modalEst = document.getElementById('modalEstudiante');
            if (event.target == modalNov) {
                modalNov.style.display = "none";
            }
            if (event.target == modalEst) {
                modalEst.style.display = "none";
            }
        }
    </script>
</body>
</html>"""
    
    html_template = html_template.replace("{time}", tiempo_actual)
    html_template = html_template.replace("{total}", str(total))
    html_template = html_template.replace("{matriculados}", str(matriculados))
    html_template = html_template.replace("{tab_buttons}", tab_buttons)
    html_template = html_template.replace("{rows}", rows)
    html_template = html_template.replace("{novedades_html}", novedades_html)
    html_template = html_template.replace("{historial_json}", historial_json)

    with open(config.HTML_NAME, "w", encoding="utf-8") as f:
        f.write(html_template)
