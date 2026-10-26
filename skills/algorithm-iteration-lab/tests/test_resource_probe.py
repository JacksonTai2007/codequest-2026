"""No games, subprocesses, or network calls are needed for these checks."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "resource_probe.py"
SPEC = importlib.util.spec_from_file_location("resource_probe", SCRIPT)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class ResourceProbeTests(unittest.TestCase):
    def plan(self, cpus=8, memory=8192, *args):
        return probe.recommend({"logical_cpus": cpus, "available_memory_mb": memory}, probe.parse_args(args))

    def test_unknown_memory(self):
        with patch.object(probe.platform, "system", return_value="UnknownOS"):
            self.assertIsNone(probe.available_memory_mb())
        result = self.plan(8, None, "--peak-memory-mb", "100")
        self.assertEqual(result["recommended_workers"], 1)
        self.assertEqual(result["memory_fit"], "unknown")

    def test_single_core(self):
        result = self.plan(1, 8192, "--peak-memory-mb", "100")
        self.assertEqual(result["recommended_workers"], 1)
        self.assertEqual(result["reserved_logical_cpus"], 0)

    def test_invalid_arguments(self):
        for args in [("--workers", "0"), ("--matches", "-1"), ("--peak-memory-mb", "nan"),
                     ("--seconds-per-match", "inf"), ("--workers", "1.5"), ("--unknown", "x")]:
            with self.subTest(args=args), contextlib.redirect_stdout(io.StringIO()) as out:
                with self.assertRaises(SystemExit) as failure:
                    probe.parse_args(args)
                self.assertEqual(failure.exception.code, 2)
                self.assertIn("error", json.loads(out.getvalue()))

    def test_insufficient_memory(self):
        result = self.plan(8, 512, "--peak-memory-mb", "128", "--matches", "4", "--seconds-per-match", "2")
        self.assertEqual(result["recommended_workers"], 0)
        self.assertIsNone(result["estimated_wall_seconds"])
        self.assertEqual(self.plan(8, 0)["recommended_workers"], 0)

    def test_extreme_numeric_inputs(self):
        result = self.plan(4, 8192, "--peak-memory-mb", "1e-323", "--matches", "100", "--seconds-per-match", "1e308")
        self.assertEqual(result["recommended_workers"], 3)
        self.assertIsNone(result["estimated_wall_seconds"])

    def test_estimate_and_reserve(self):
        result = self.plan(4, 8192, "--peak-memory-mb", "512", "--matches", "10", "--seconds-per-match", "2")
        self.assertEqual(result["recommended_workers"], 3)
        self.assertEqual(result["reserved_logical_cpus"], 1)
        self.assertEqual(result["estimated_wall_seconds"], 8)
        self.assertFalse(result["estimate_is_measured"])
        self.assertEqual(self.plan(8, 8192, "--workers", "2", "--peak-memory-mb", "512")["recommended_workers"], 2)

    def test_linux_memory_and_failure(self):
        with patch.object(probe.platform, "system", return_value="Linux"):
            with patch.object(probe.Path, "read_text", return_value="MemAvailable: 2097152 kB\n"):
                self.assertEqual(probe.available_memory_mb(), 2048)
            with patch.object(probe.Path, "read_text", side_effect=OSError):
                self.assertIsNone(probe.available_memory_mb())

    def test_no_args_json_inventory(self):
        with patch.object(probe.os, "cpu_count", return_value=None), \
             patch.object(probe, "available_memory_mb", return_value=None), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            probe.main([])
        data = json.loads(out.getvalue())
        self.assertIsNone(data["inventory"]["logical_cpus"])
        self.assertEqual(data["inventory"]["memory_status"], "unknown")
        self.assertIsNone(data["plan"]["estimated_wall_seconds"])


if __name__ == "__main__":
    unittest.main()
