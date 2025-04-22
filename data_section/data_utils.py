import pickle
from show_message import show_message

def save_lap_data(lap_telemetry, lap_times, filename="data_section/telemetry_data.pkl"):
    with open(filename, "wb") as f:
        pickle.dump({"laps": lap_telemetry, "times": lap_times}, f)
    show_message(f"Telemetriai adatok mentve: {filename}")


def load_lap_data(filename="data_section/telemetry_data.pkl"):
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
            show_message(f"Telemetriai adatok betöltve: {filename}")
            return data["laps"], data["times"]
    except FileNotFoundError:
        show_message("Nincsenek mentett telemetriai adatok!")
        return {}, {}
