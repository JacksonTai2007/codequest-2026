"""Read-only host inventory and conservative planning; never runs benchmarks."""

import argparse
import ctypes
import json
import math
import os
import platform
from pathlib import Path


def available_memory_mb():
    """Return available physical memory in MiB, or None without guessing."""
    try:
        if platform.system() == "Windows":
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_uint32), ("load", ctypes.c_uint32)] + [
                    (name, ctypes.c_uint64) for name in (
                        "total_phys", "avail_phys", "total_page", "avail_page",
                        "total_virtual", "avail_virtual", "avail_extended")]
            status = MemoryStatus()
            status.length = ctypes.sizeof(status)
            query = ctypes.WinDLL("kernel32", use_last_error=True).GlobalMemoryStatusEx
            query.argtypes = [ctypes.POINTER(MemoryStatus)]
            query.restype = ctypes.c_int
            if query(ctypes.byref(status)):
                return status.avail_phys / (1024 * 1024)
        elif platform.system() == "Linux":
            for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
                parts = line.split()
                if len(parts) == 3 and parts[0] == "MemAvailable:" and parts[2] == "kB":
                    value = int(parts[1])
                    return value / 1024 if value >= 0 else None
    except (OSError, ValueError, AttributeError, OverflowError):
        pass
    return None


def inventory():
    cpus = os.cpu_count()
    memory = available_memory_mb()
    return {
        "platform": platform.system(), "logical_cpus": cpus,
        "available_memory_mb": memory, "memory_unit": "MiB",
        "memory_status": "unknown" if memory is None else "observed",
        "measurement_scope": "host snapshot; container/job quotas may be lower",
        "cpu_note": "Logical core count is not a performance measurement.",
    }


def recommend(host, args):
    cpus, available = host["logical_cpus"], host["available_memory_mb"]
    reserved_cores = 1 if cpus and cpus > 1 else 0
    cpu_cap = max(1, cpus - reserved_cores) if cpus else 1
    reserved_mb = max(1024.0, available * 0.25) if available is not None else None
    usable_mb = max(0.0, available - reserved_mb) if available is not None else None
    reasons = []
    if available is not None and args.peak_memory_mb is not None:
        # Clamp before dividing so tiny positive user inputs cannot overflow.
        memory_cap = cpu_cap if usable_mb >= args.peak_memory_mb * cpu_cap else int(usable_mb // args.peak_memory_mb)
        memory_fit = "estimated_from_user_peak"
    else:
        memory_cap = 0 if usable_mb == 0 else 1
        memory_fit = "unknown"
        reasons.append("Memory or per-match peak is unknown: cap at most one worker; fit is unverified.")
    workers = min(cpu_cap, memory_cap)
    if args.workers is not None:
        workers = min(workers, args.workers)
    if args.matches is not None:
        workers = min(workers, args.matches)
    seconds = None
    if workers == 0:
        reasons.append("Insufficient available memory after the safety reserve; do not start a worker.")
    elif args.matches is not None and args.seconds_per_match is not None:
        try:
            batches = (args.matches + workers - 1) // workers
            estimate = batches * args.seconds_per_match
            seconds = estimate if math.isfinite(estimate) else None
        except OverflowError:
            pass
        if seconds is None:
            reasons.append("Wall-clock estimate exceeds numeric range.")
    else:
        reasons.append("Provide --matches and --seconds-per-match to estimate wall-clock time.")
    return {
        "recommended_workers": workers, "reserved_logical_cpus": reserved_cores,
        "reserved_memory_mb": reserved_mb, "memory_fit": memory_fit,
        "estimated_wall_seconds": seconds, "estimate_is_measured": False,
        "estimate_assumptions": "ceil(matches/workers) * supplied seconds; equal independent jobs; "
                                "no startup, contention, or throttling costs; not a guarantee",
        "notes": reasons,
    }


def positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return number


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


class JsonParser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps({"error": message}))
        raise SystemExit(2)


def parse_args(argv=None):
    parser = JsonParser(description=__doc__)
    parser.add_argument("--seconds-per-match", type=positive_float, help="Supplied measured seconds per job")
    parser.add_argument("--peak-memory-mb", type=positive_float, help="Supplied per-worker peak RSS in MiB")
    parser.add_argument("--matches", type=positive_int, help="Number of independent jobs")
    parser.add_argument("--workers", type=positive_int, help="Upper limit, never a request to run jobs")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    host = inventory()
    print(json.dumps({"inventory": host, "inputs": vars(args), "plan": recommend(host, args)},
                     indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
