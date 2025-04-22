import tkinter as tk
import numpy as np
from track_sections.track_sections import TRACK_SECTIONS


FEATURES = {"Speed": 1, "RPM": 2, "Throttle": 3, "Brake": 4, "Steering": 5}

SECTION_ADVICE = {
    "straight": {
        "Speed":      {"unit": "km/h", "more": "", "less": ""},
        "RPM":        {"unit": "",     "more": " → válts később az egyenesekben, forgasd ki jobban a motort.", "less": " → válts korábban az egyenesekben, ne forgasd ki annyira a motort."},
        "Throttle":   {"unit": "",     "more": " → előbb állj padlógázra", "less": " → óvatosabban emeld a gáz mértékét padlógázig"},
        "Brake":      {"unit": "",     "more": " → fékezz erősebben, később csökkentsd a fékerőt", "less": " → fékezz óvatosabban, korábban kezd csökkenteni a fékerőt"},
        "Steering":   {"unit": "",     "more": " → fordítsd el jobban a kormányt (nagyobb kormányszög)", "less": " → kevésbé fordítsd el a kormányt (kisebb kormányszög)"}
    },
    "braking": {
        "Speed":      {"unit": "km/h", "more": " → próbálj nagyobb sebességgel bemenni a kanyarba", "less": " → próbálj kisebb sebességre lassítani a kanyar előtt"},
        "RPM":        {"unit": "",     "more": " → előbb válts alacsonyabb fokozatra a leváltásnál fékezés közben", "less": " → magasabb sebességi fokozatban menj be a kanyarba"},
        "Throttle":   {"unit": "",     "more": " → később lépj le a gázról a féktáv előtt", "less": " → előbb lépj le a gázról a féktáv előtt"},
        "Brake":      {"unit": "",     "more": " → fékezz erősebben, később csökkentsd a fékerőt", "less": " → fékezz óvatosabban, korábban kezd csökkenteni a fékerőt"},
        "Steering":   {"unit": "",     "more": " → fordítsd el jobban a kormányt fékezés közben (nagyobb kormányszög)", "less": " → kevésbé fordítsd el a kormányt fékezés közben (kisebb kormányszög)"}
    },
    "apex": {
        "Speed":      {"unit": "km/h", "more": " → próbálj nagyobb sebességgel elfordulni a csúcsponton", "less": " → próbálj meg kisebb sebességgel átmenni a csúcsponton"},
        "RPM":        {"unit": "",     "more": " → kisebb sebességi fokozatban vedd be a kanyart", "less": " → magasabb sebességi fokozatban vedd be a kanyart"},
        "Throttle":   {"unit": "",     "more": " → nagyobb gázállással fordulj a kanyarcsúcspontnál", "less": " → kisebb gázállással fordulj a kanyarcsúcspontnál"},
        "Brake":      {"unit": "",     "more": " → tartsd magasabban a fékerőt a kanyarcsúcspontnál", "less": " → próbálj meg kevesebb fékerőt a kanyarcsúcspontnál"},
        "Steering":   {"unit": "",     "more": " → fordítsd el jobban a kormányt a kanyarcsúcsponton (nagyobb kormányszög)", "less": " → kevésbé fordítsd el a kormányt a kanyarcsúcsponton (kisebb kormányszög)"}
    },
    "acceleration": {
        "Speed":      {"unit": "km/h", "more": " → próbáld nagyobb minimumtempóról megkezdeni a kigyorsítást", "less": " → próbáld kisebb minimumtempóról megkezdeni a kigyorsítást"},
        "RPM":        {"unit": "",     "more": " → próbálj meg kisebb sebességi fokozatban kigyorsítani", "less": " → próbálj meg magasabb sebességi fokozatban kigyorsítani"},
        "Throttle":   {"unit": "",     "more": " → előbb kezd el emelni a gázállást a kigyorsításnál", "less": " → később kezd el emelni a gázállást a kigyorsításnál"},
        "Brake":      {"unit": "",     "more": " → alkalmazz nagyobb fékerőt a kigyorsítás előtt", "less": " → figyelj, hogy a kigyorsításnál egyáltalán ne nyomd a fékpedált"},
        "Steering":   {"unit": "",     "more": " → fordítsd el jobban a kormányt a kigyorsításnál (nagyobb kormányszög)", "less": " → kevésbé fordítsd el a kormányt a kigyorsítás közben (kisebb kormányszög)"}
    }
}


def extract_section_data(lap_telemetry, lap_times, section_type):
    section_results = []
    for section in TRACK_SECTIONS:
        if section["type"] != section_type:
            continue
        section_name = section["name"]
        features_per_lap = []
        lap_ids = []
        for lap, points in lap_telemetry.items():
            values = [pt for pt in points if section["start"] <= pt[0] <= section["end"]]
            if not values:
                continue
            avg = np.mean([[pt[FEATURES["Speed"]],
                            pt[FEATURES["RPM"]],
                            pt[FEATURES["Throttle"]],
                            pt[FEATURES["Brake"]],
                            pt[FEATURES["Steering"]]] for pt in values], axis=0)
            features_per_lap.append(avg)
            lap_ids.append(lap)
        if len(features_per_lap) >= 2:
            section_results.append((section_name, np.array(features_per_lap), lap_ids))
    return section_results


def analyze_section(section_name, features, lap_ids, lap_times, section_type):
    advice_cfg = SECTION_ADVICE.get(section_type, {})
    fastest_lap = min(lap_ids, key=lambda l: lap_times.get(l, float("inf")))
    fastest_idx = lap_ids.index(fastest_lap)
    fastest_values = features[fastest_idx]
    text = f"{section_name} – Átlagos eltérés a leggyorsabb körhöz (Kör {fastest_lap}) képest:\n"
    for i, name in enumerate(["Speed", "RPM", "Throttle", "Brake", "Steering"]):
        if name not in advice_cfg:
            continue
        others = [features[j][i] for j in range(len(features)) if j != fastest_idx]
        avg_other = np.mean(others)
        diff = avg_other - fastest_values[i]
        if abs(diff) < 0.01:
            continue
        direction = "Több" if diff < 0 else "Kevesebb"
        unit = advice_cfg[name].get("unit", "")
        postfix = advice_cfg[name]["more" if diff < 0 else "less"]
        if name == "RPM":
            value = f"{int(round(diff)):+}"
        elif name == "Speed":
            value = f"{diff:+.2f} {unit}"
        else:
            value = f"{diff:+.2f}"
        text += f"  - {direction} {name.lower()} segíthet (eltérés: {value}){postfix}\n"
    text += "\n"
    return text


def run_cart_analysis_with_feedback(lap_telemetry, lap_times, section_type="straight"):
    results = extract_section_data(lap_telemetry, lap_times, section_type)
    if not results:
        return
    full_text = f"CART döntési fa elemzés – {section_type.capitalize()} szakaszok\n\n"
    for section_name, features, lap_ids in results:
        full_text += analyze_section(section_name, features, lap_ids, lap_times, section_type)
    show_feedback_window(full_text)


def show_feedback_window(text):
    window = tk.Toplevel()
    window.title("CART algoritmus – szakaszonkénti visszajelzés")
    txt = tk.Text(window, wrap="word", width=95, height=30)
    txt.insert(tk.END, text)
    txt.pack(padx=10, pady=10)
