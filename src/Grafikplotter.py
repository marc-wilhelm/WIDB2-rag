from typing import List, Dict, Optional, Callable, Any
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
from IPython.display import HTML

def grafik_plotten_dynamisch(
    labels: Dict[str, str],         # Labels für x und y (z.B. {"x": "Monat", "y": "Umsatz"})
    values: Dict[str, Any],         # Daten-Dictionary
    units: List[str],               # Liste der Business Units (z.B. ["Home Tech"])
    title: str = "",                # Diagrammtitel
    animate: bool = True,           # Animation an/aus
):
    """
    Plottet Daten chronologisch sortiert nach deutschen Monaten.
    """
    # -------------------------------
    # 1. Validierung
    # -------------------------------
    if "x" not in labels or "y" not in labels:
        raise KeyError("labels muss die Schlüssel 'x' und 'y' enthalten")
    if not values or not units:
        raise ValueError("values und units dürfen nicht leer sein")

    # -------------------------------
    # 2. Datenstruktur normalisieren
    # -------------------------------
    normalized_values = {}
    
    # Falls Claude die Daten flach liefert (nur eine Unit)
    if len(units) == 1:
        unit_name = units[0]
        if unit_name not in values:
            normalized_values = {unit_name: values}
        else:
            normalized_values = values
    else:
        normalized_values = values

    # -------------------------------
    # 3. Daten vorbereiten & Chronologisch sortieren
    # -------------------------------
    all_x_keys = set()
    for unit in units:
        if unit in normalized_values:
            all_x_keys.update(normalized_values[unit].keys())
    
    # Mapping für deutsche Monatsnamen zur korrekten Sortierung
    monats_reihenfolge = {
        "Januar": 1, "Februar": 2, "März": 3, "April": 4, 
        "Mai": 5, "Juni": 6, "Juli": 7, "August": 8, 
        "September": 9, "Oktober": 10, "November": 11, "Dezember": 12
    }

    def sort_key(x_value):
        # 1. Versuch: Handelt es sich um einen bekannten Monatsnamen?
        if str(x_value) in monats_reihenfolge:
            return monats_reihenfolge[str(x_value)]
        
        # 2. Versuch: Handelt es sich um ein ISO-Datum (YYYY-MM-DD)?
        try:
            return datetime.fromisoformat(str(x_value)).timestamp()
        except:
            pass
            
        # 3. Fallback: Gib den Wert als String zurück (alphabetisch)
        return str(x_value)

    # Sortiere die X-Achse nach unserer Logik
    x_raw = sorted(list(all_x_keys), key=sort_key)
    x_formatted = [str(x) for x in x_raw]

    # Y-Daten für jede Unit sammeln
    unit_data = {}
    max_y = 0
    for unit in units:
        y_values = []
        data_for_unit = normalized_values.get(unit, {})
        for x_key in x_raw:
            y_val = data_for_unit.get(x_key, 0)
            if y_val is None: y_val = 0
            y_values.append(y_val)
            max_y = max(max_y, y_val)
        unit_data[unit] = y_values

    # -------------------------------
    # 4. Plot erstellen
    # -------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
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
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Achsengrenzen
    ax.set_xlim(-0.5, len(x_formatted) - 0.5)
    ax.set_ylim(0, max_y * 1.2 if max_y > 0 else 10)

    # X-Achse beschriften
    ax.set_xticks(range(len(x_formatted)))
    ax.set_xticklabels(x_formatted, rotation=45, ha='right')

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', framealpha=0.9)
    plt.tight_layout()

    # -------------------------------
    # 5. Animation oder statisch
    # -------------------------------
    if animate:
        def update(frame):
            for unit in units:
                # Zeige Daten bis zum aktuellen Frame
                curr_x = range(frame + 1)
                curr_y = unit_data[unit][:frame + 1]
                lines[unit].set_data(curr_x, curr_y)
            return list(lines.values())

        anim = FuncAnimation(
            fig, 
            update, 
            frames=len(x_formatted), 
            interval=300, 
            blit=True, 
            repeat=False
        )
        
        try:
            plt.close() # Verhindert statische Anzeige in Notebooks
            return HTML(anim.to_jshtml())
        except:
            return anim
    else:
        # Falls keine Animation gewünscht, zeichne alles sofort
        for unit in units:
            lines[unit].set_data(range(len(x_formatted)), unit_data[unit])
        return fig, ax