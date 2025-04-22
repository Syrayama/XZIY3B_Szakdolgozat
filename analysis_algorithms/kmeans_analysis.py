import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from track_sections.track_sections import TRACK_SECTIONS
import tkinter as tk
from tkinter import scrolledtext
from collections import defaultdict


lap_cluster_labels = {}

def show_feedback_window(title, content):
    feedback_win = tk.Toplevel()
    feedback_win.title(title)
    txt = scrolledtext.ScrolledText(feedback_win, width=80, height=25)
    txt.insert(tk.INSERT, content)
    txt.pack(padx=10, pady=10)


def run_kmeans_analysis_with_feedback(lap_telemetry, lap_times, selected_laps, section_type="straight", n_clusters=3):
    feature_names_map = {
        "straight": ["Kormányszög", "Sebesség", "Gázállás"],
        "braking": ["Fék", "Sebesség", "Kormányszög"],
        "apex": ["Kormányszög", "Sebesség", "Fék"],
        "acceleration": ["Gáz", "Sebesség", "Kormányszög"]
    }

    feature_indices = {
        "straight":     ([5, 1, 3], "Kormányszög", "Sebesség"),
        "braking":      ([4, 1, 5], "Fékállás", "Sebesség"),
        "apex":         ([5, 1, 4], "Kormányszög", "Sebesség"),
        "acceleration": ([3, 1, 5], "Gázállás", "Sebesség")
    }

    if not selected_laps:
        return "Nincs kiválasztott kör az elemzéshez."
    if section_type not in feature_indices:
        return f"Ismeretlen szakasztípus: {section_type}"
    indices, xlabel, ylabel = feature_indices[section_type]
    feature_names = feature_names_map[section_type]
    samples = []
    sample_lap_ids = []
    for lap in selected_laps:
        if lap not in lap_telemetry:
            continue
        for pt in lap_telemetry[lap]:
            distance = pt[0]
            for section in TRACK_SECTIONS:
                if section["type"] == section_type and section["start"] <= distance <= section["end"]:
                    sample = [pt[i] for i in indices]
                    samples.append(sample)
                    sample_lap_ids.append(lap)
                    break
    if len(samples) < n_clusters:
        return f"Nincs elég adat a(z) {section_type} szakaszhoz (csak {len(samples)} adatpont). Rögzítsd több kör adatát."
    X = np.array(samples)
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    kmeans.fit(X)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_
    plt.figure(figsize=(8, 5))
    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', alpha=0.6)
    plt.scatter(centers[:, 0], centers[:, 1], c='red', s=120, marker='X', label='Középpontok')
    for i, (x, y) in enumerate(centers[:, :2]):
        plt.text(x, y, f"K{i}", fontsize=10, color="black", weight="bold")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"K-means klaszterezés – {section_type.capitalize()} szakasz")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    cluster_laps = defaultdict(set)
    for lap_id, label in zip(sample_lap_ids, labels):
        cluster_laps[label].add(lap_id)

    cluster_avg_times = {}
    for cluster_id, laps in sorted(cluster_laps.items()):
        times = [lap_times[lap] for lap in laps if lap in lap_times]
        cluster_avg_times[cluster_id] = np.mean(times) if times else float('inf')
    feedback = f"K-means klaszterek – {section_type.capitalize()} szakasz\n"
    if len(cluster_avg_times) >= 2:
        sorted_clusters = sorted(cluster_avg_times.items(), key=lambda x: x[1])
        best_cluster_id = sorted_clusters[0][0]
        worst_cluster_id = sorted_clusters[-1][0]
        feedback += f"\nLeggyorsabb klaszter: {best_cluster_id}, Leglassabb klaszter: {worst_cluster_id}\n"
        diffs = centers[worst_cluster_id] - centers[best_cluster_id]
        feedback += f"\nTanácsok a köridő javításához:\n"
        for i, diff in enumerate(diffs):
            if abs(diff) < 0.01:
                continue
            direction = "Nagyobb átlagos" if diff < 0 else "Kisebb átlagos"
            feedback += f"   - {direction} {feature_names[i].lower()} lehet az eredményesebb vezetési stílus.\n"
    show_feedback_window(f"K-means elemzés – {section_type.capitalize()}", feedback)