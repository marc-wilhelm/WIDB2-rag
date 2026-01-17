from typing import List, Dict, Optional, Callable, Any
import anthropic
from VectoreStoreManager import VectorStoreManager
import config
import json
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
from IPython.display import HTML


def grafik_plotten_dynamisch(
    labels: dict[str, str],
    values: dict,
    units: list[str],
    title: str = "",
    animate: bool = True,
):
    """
    Plottet Daten dynamisch mit optionaler Animation.
    
    Args:
        labels: Dictionary mit 'x' und 'y' Keys für Achsenbeschriftungen
        values: Dictionary mit x-Werten als Keys und y-Werten als Values,
                bei mehreren units: {unit: {x: y, ...}, ...}
                bei einer unit: {x: y, ...} (unverschachtelt möglich)
        units: Liste mit Einheiten (z.B. ['Home Tech', 'Digital Solutions'])
        title: Titel des Plots
        animate: Ob Animation verwendet werden soll (True) oder statischer Plot (False)
        
    Beispiele:
        # Eine Unit (unverschachtelt)
        values = {'2024-01-01': 100, '2024-02-01': 150}
        units = ['Home Tech']
        
        # Mehrere Units (verschachtelt)
        values = {
            'Home Tech': {'2024-01-01': 100, '2024-02-01': 150},
            'Digital Solutions': {'2024-01-01': 80, '2024-02-01': 120}
        }
        units = ['Home Tech', 'Digital Solutions']
    """
    # -------------------------------
    # 1. Validierung
    # -------------------------------
    if "x" not in labels or "y" not in labels:
        raise KeyError("labels muss die Schlüssel 'x' und 'y' enthalten")
    if not values:
        raise ValueError("values darf nicht leer sein")
    if not units:
        raise ValueError("units darf nicht leer sein")
    
    valid_units = {"Home Tech", "Digital Solutions"}
    if not set(units).issubset(valid_units):
        raise ValueError(f"Ungültige units. Erlaubt sind: {valid_units}")
    
    # -------------------------------
    # 2. Datenstruktur normalisieren
    # -------------------------------
    # Prüfen ob verschachtelt oder unverschachtelt
    if len(units) == 1 and units[0] not in values:
        # Unverschachtelt: {x: y, ...} -> {unit: {x: y, ...}}
        normalized_values = {units[0]: values}
    else:
        # Verschachtelt: bereits im richtigen Format
        normalized_values = values
        # Validierung: alle units müssen vorhanden sein
        for unit in units:
            if unit not in normalized_values:
                raise ValueError(f"Unit '{unit}' nicht in values gefunden")
    
    # -------------------------------
    # 3. Daten vorbereiten
    # -------------------------------
    # Gemeinsame X-Achse aus allen Units erstellen
    all_x_keys = set()
    for unit in units:
        all_x_keys.update(normalized_values[unit].keys())
    
    x_raw = sorted(list(all_x_keys))
    
    # Zeitstempel parsen und formatieren
    x_formatted = []
    for v in x_raw:
        if isinstance(v, str):
            try:
                x_formatted.append(datetime.fromisoformat(v).strftime('%d/%m/%Y'))
            except:
                x_formatted.append(str(v))
        elif isinstance(v, datetime):
            x_formatted.append(v.strftime('%d/%m/%Y'))
        else:
            x_formatted.append(str(v))
    
    # Y-Daten für jede Unit vorbereiten
    unit_data = {}
    max_y = 0
    for unit in units:
        y_values = []
        for x_key in x_raw:
            y_val = normalized_values[unit].get(x_key, None)
            y_values.append(y_val)
            if y_val is not None:
                max_y = max(max_y, y_val)
        
        # Validierung: numerische Werte
        for v in y_values:
            if v is not None and not isinstance(v, (int, float)):
                raise ValueError(f"Alle Werte müssen numerisch sein oder None")
        
        unit_data[unit] = y_values
    
    # -------------------------------
    # 4. Plot erstellen
    # -------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Farben für verschiedene Units
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    lines = {}
    
    for i, unit in enumerate(units):
        color = colors[i % len(colors)]
        line, = ax.plot([], [], marker="o", linewidth=2, markersize=8, 
                       label=unit, color=color, alpha=0.9)
        lines[unit] = line
    
    ax.set_xlabel(labels["x"], fontsize=12)
    ax.set_ylabel(labels["y"], fontsize=12)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', loc="center")
    
    # Achsengrenzen setzen
    ax.set_xlim(-0.5, len(x_formatted) - 0.5)
    ax.set_ylim(0, max_y * 1.15 if max_y > 0 else 10)
    
    # X-Achse mit formatierten Labels
    ax.set_xticks(range(len(x_formatted)))
    ax.set_xticklabels(x_formatted, rotation=45, ha='right')
    
    # Grid hinzufügen
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Legende hinzufügen
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    
    plt.tight_layout()
    
    # -------------------------------
    # 5. Animation oder statischer Plot
    # -------------------------------
    if animate:
        # Animation: Daten werden schrittweise angezeigt
        def init():
            for line in lines.values():
                line.set_data([], [])
            return list(lines.values())
        
        def update(frame):
            result = []
            points_per_unit = len(x_formatted)
            
            for idx, unit in enumerate(units):
                # Berechne den Start-Frame für diese Unit
                start_frame = idx * points_per_unit
                end_frame = start_frame + points_per_unit
                
                if frame < start_frame:
                    # Diese Unit hat noch nicht begonnen
                    lines[unit].set_data([], [])
                elif frame >= end_frame:
                    # Diese Unit ist komplett
                    x_data = []
                    y_data = []
                    for i in range(points_per_unit):
                        if unit_data[unit][i] is not None:
                            x_data.append(i)
                            y_data.append(unit_data[unit][i])
                    lines[unit].set_data(x_data, y_data)
                else:
                    # Diese Unit wird gerade animiert
                    current_point = frame - start_frame
                    x_data = []
                    y_data = []
                    for i in range(current_point + 1):
                        if unit_data[unit][i] is not None:
                            x_data.append(i)
                            y_data.append(unit_data[unit][i])
                    lines[unit].set_data(x_data, y_data)
                
                result.append(lines[unit])
            return result
        
        anim = FuncAnimation(
            fig, 
            update, 
            init_func=init,
            frames=len(x_formatted) * len(units),
            interval=150,
            blit=False,
            repeat=False
        )
        
        # Für Jupyter Notebook
        try:
            plt.close()  # Verhindert doppelte Anzeige
            return HTML(anim.to_jshtml())
        except:
            # Für normale Python-Umgebung
            plt.show()
            return anim
    else:
        # Statischer Plot: Alle Daten sofort anzeigen
        for unit in units:
            x_data = []
            y_data = []
            for i, y_val in enumerate(unit_data[unit]):
                if y_val is not None:
                    x_data.append(i)
                    y_data.append(y_val)
            lines[unit].set_data(x_data, y_data)
        #plt.show()
        return fig, ax


