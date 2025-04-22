import unittest
import numpy as np
import os
from unittest.mock import patch
from data_section.data_utils import save_lap_data, load_lap_data
from data_section.udp_listener import lap_telemetry, lap_times
from analysis_algorithms.cart_feedback import extract_section_data


class TestTelemetrySystem(unittest.TestCase):


    def test_udp_listener_initial_state(self):
        self.assertIsInstance(lap_telemetry, dict)
        self.assertIsInstance(lap_times, dict)


    def test_save_and_load_data(self):
        test_data = {0: [(0, 200, 10000, 1.0, 0.0, 0.0)]}
        test_times = {0: 62000}
        test_file = "test_temp.pkl"
        save_lap_data(test_data, test_times, filename=test_file)
        loaded_data, loaded_times = load_lap_data(filename=test_file)
        self.assertEqual(test_data, loaded_data)
        self.assertEqual(test_times, loaded_times)
        os.remove(test_file)

    def test_kmeans_fails_with_insufficient_data(self):
        telemetry, times = load_lap_data(filename="test_data.pkl")
        laps = list(telemetry.keys())
        import analysis_algorithms.kmeans_analysis as km_mod
        with patch.object(km_mod.plt, "show", lambda: None), \
                patch.object(km_mod, "show_feedback_window", lambda title, content: None):
            result = km_mod.run_kmeans_analysis_with_feedback(telemetry, times, laps, section_type="braking", n_clusters=3)
            expected_message = "Nincs elég adat a(z) braking szakaszhoz"
            self.assertIsInstance(result, str)
            self.assertTrue(result.startswith(expected_message))


    def test_cart_extract_sections_from_real_data(self):
        telemetry, times = load_lap_data(filename="../data_section/telemetry_data.pkl")
        result = extract_section_data(telemetry, times, section_type="braking")
        self.assertTrue(len(result) > 0)
        self.assertIsInstance(result[0][1], np.ndarray)


if __name__ == "__main__":
    unittest.main()
