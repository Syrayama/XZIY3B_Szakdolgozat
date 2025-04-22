import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import CheckButtons, RadioButtons, Button
from analysis_algorithms.kmeans_analysis import run_kmeans_analysis_with_feedback
from data_section.data_utils import save_lap_data, load_lap_data
from data_section.udp_listener import start_udp_listener, stop_udp_listener, lap_telemetry, lap_times
from analysis_algorithms.cart_feedback import run_cart_analysis_with_feedback, show_feedback_window


selected_laps = []
selected_metric = "Speed"

fig = plt.figure(figsize=(17, 7))

main_ax = fig.add_axes([0.25, 0.1, 0.70, 0.80])
main_ax.set_xlabel("Pálya távolság (m)")
main_ax.grid(True)
main_ax.set_xlim(0, 4326)

radio_ax = fig.add_axes([0.02, 0.25, 0.1, 0.2])
check_ax = fig.add_axes([0.02, 0.55, 0.1, 0.4])

section_ax = fig.add_axes([0.02, 0.02, 0.08, 0.04])
section_button = Button(section_ax, 'Elemzés')
section_button.on_clicked(lambda event: open_section_analysis_window())

def on_save_click(event):
    stop_udp_listener()
    save_lap_data(lap_telemetry, lap_times)

def on_load_click(event):
    laps, times = load_lap_data()
    lap_telemetry.clear()
    lap_telemetry.update(laps)
    lap_times.clear()
    lap_times.update(times)
    update_check_buttons()

listener_ax = fig.add_axes([0.02, 0.17, 0.1, 0.04])
listener_button = Button(listener_ax, 'Adatfogadás indítása')
listener_button.on_clicked(lambda event: start_udp_listener())

save_ax = fig.add_axes([0.02, 0.07, 0.08, 0.04])
save_button = Button(save_ax, 'Mentés')
save_button.on_clicked(on_save_click)

load_ax = fig.add_axes([0.02, 0.12, 0.08, 0.04])
load_button = Button(load_ax, 'Betöltés')
load_button.on_clicked(on_load_click)

radio_ax.set_xticks([])
radio_ax.set_yticks([])

metrics = ["Speed", "RPM", "Throttle", "Brake", "Steering"]
radio = RadioButtons(radio_ax, metrics, active=0)
selected_metric = "Speed"


def on_metric_change(label):
    global selected_metric
    selected_metric = label
    fig.canvas.draw_idle()

radio.on_clicked(on_metric_change)
check_buttons = None

def format_lap_time(ms):
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"


def update_check_buttons():
    global check_buttons, selected_laps
    available = sorted(lap_telemetry.keys())
    labels = [f"{lap} – {format_lap_time(lap_times.get(lap, 0))}" for lap in available]
    visibility = [lap in selected_laps for lap in available]
    check_ax.cla()
    check_ax.set_xticks([])
    check_ax.set_yticks([])
    check_buttons = CheckButtons(check_ax, labels, visibility)
    def on_click(label):
        lap = int(label.split("–")[0].strip())
        if lap in selected_laps:
            selected_laps.remove(lap)
        else:
            selected_laps.append(lap)
        selected_laps.sort()
        fig.canvas.draw_idle()
    check_buttons.on_clicked(on_click)
    fig.canvas.draw_idle()


def set_y_axis(ax):
    global selected_metric
    if selected_metric == "Speed":
        ax.set_ylabel("Sebesség (km/h)")
        ax.set_ylim(0, 360)
    elif selected_metric == "RPM":
        ax.set_ylabel("RPM")
        ax.set_ylim(0, 14000)
    elif selected_metric in ["Throttle", "Brake"]:
        ax.set_ylabel(selected_metric)
        ax.set_ylim(0, 1.2)
    elif selected_metric == "Steering":
        ax.set_ylabel("Jobb  -  Kormányszög  -  Bal")
        ax.set_ylim(1, -1)
    else:
        ax.set_ylabel("Érték")
        ax.set_ylim(0, 1.1)


def init():
    return []


def update_plot(frame):
    update_check_buttons()
    main_ax.cla()
    main_ax.set_xlabel("Pálya távolság (m)")
    set_y_axis(main_ax)
    main_ax.set_title("F1 24 – Kiválasztott körök telemetriai adatai")
    main_ax.grid(True)
    tick_positions = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4326]
    main_ax.set_xticks(tick_positions)
    main_ax.set_xticklabels([str(tp) for tp in tick_positions])
    main_ax.set_xlim(0, 4326)
    if selected_laps:
        for lap in selected_laps:
            if lap in lap_telemetry and len(lap_telemetry[lap]) > 0:
                points = lap_telemetry[lap]
                x_vals = [pt[0] for pt in points]
                if selected_metric == "Speed":
                    y_vals = [pt[1] for pt in points]
                elif selected_metric == "RPM":
                    y_vals = [pt[2] for pt in points]
                elif selected_metric == "Throttle":
                    y_vals = [pt[3] for pt in points]
                elif selected_metric == "Brake":
                    y_vals = [pt[4] for pt in points]
                elif selected_metric == "Steering":
                    y_vals = [pt[5] for pt in points]
                else:
                    y_vals = [0 for _ in points]
                main_ax.plot(x_vals, y_vals, label=f"Kör {lap}")
    handles, labels = main_ax.get_legend_handles_labels()
    if handles:
        main_ax.legend(handles, labels)
    return main_ax.lines

ani = animation.FuncAnimation(fig, update_plot, init_func=init, interval=50, cache_frame_data=False)

def open_section_analysis_window():
    def run_analysis():
        selected = combo.get()
        section_type = selected.lower()
        result = run_kmeans_analysis_with_feedback(lap_telemetry, lap_times, selected_laps, section_type=section_type)
        if result:show_feedback_window(result)
        run_cart_analysis_with_feedback(lap_telemetry, lap_times, section_type=section_type)
        window.destroy()

    window = tk.Tk()
    window.title("Szakasz kiválasztása")
    tk.Label(window, text="Válassz szakaszt az elemzéshez:").pack(padx=10, pady=5)

    options = ["straight", "braking", "apex", "acceleration"]
    combo = ttk.Combobox(window, values=options)
    combo.current(0)
    combo.pack(padx=10, pady=5)

    start_btn = tk.Button(window, text="Elemzés indítása", command=run_analysis)
    start_btn.pack(padx=10, pady=10)

    window.mainloop()


main_ax.format_coord = lambda x, y: f"(x, y) = ({x:.1f}, {y:.3f})"
plt.show()