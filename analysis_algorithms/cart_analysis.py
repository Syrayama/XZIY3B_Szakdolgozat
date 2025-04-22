import numpy as np
from sklearn.tree import DecisionTreeRegressor
from track_sections.track_sections import TRACK_SECTIONS


def run_cart_model_per_section(lap_telemetry, lap_times, section_type="braking"):
    results = []
    for section in TRACK_SECTIONS:
        if section["type"] != section_type:
            continue
        section_name = section["name"]
        features = []
        targets = []
        for lap in lap_telemetry:
            if lap not in lap_times:
                continue
            points = [pt for pt in lap_telemetry[lap] if section["start"] <= pt[0] <= section["end"]]
            if not points:
                continue
            avg = np.mean([[pt[1], pt[2], pt[3], pt[4], pt[5]] for pt in points], axis=0)
            features.append(avg)
            targets.append(lap_times[lap])
        if len(features) < 3:
            continue
        X = np.array(features)
        y = np.array(targets)
        model = DecisionTreeRegressor(max_depth=12, random_state=42)
        model.fit(X, y)

        results.append({
            "name": section_name,
            "model": model,
            "feature_names": ["Speed", "RPM", "Throttle", "Brake", "Steering"]
        })

    return results