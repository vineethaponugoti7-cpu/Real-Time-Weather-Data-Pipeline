"""
Local weather pipeline (no AWS required).

Fetches current weather for a list of cities from OpenWeatherMap, prints a
live console table, and saves each reading as a JSON file in the output
directory — mirroring what the AWS/S3 version stores in the cloud.

Run:
    python src/pipeline_local.py            # loops every POLL_INTERVAL_SEC
    python src/pipeline_local.py --once     # single pass, then exit
"""

import argparse
import json
import os
import time

import config
from weather import fetch_weather


def save_record(record: dict, output_dir: str) -> str:
    """Save one weather record as a JSON file; return the file path."""
    os.makedirs(output_dir, exist_ok=True)
    # Safe filename: city + timestamp, with characters that break paths removed.
    safe_city = record["city"].replace(" ", "_").replace("/", "-")
    safe_time = record["timestamp"].replace(":", "-")
    path = os.path.join(output_dir, f"{safe_city}_{safe_time}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    return path


def print_header() -> None:
    print(f"\n{'City':<15} {'Temp (C)':>9} {'Humidity':>9} {'Wind':>6}  {'Weather':<12} {'Time (UTC)'}")
    print("-" * 78)


def print_row(record: dict) -> None:
    ts = record["timestamp"].replace("T", " ").split(".")[0]
    print(
        f"{record['city']:<15} "
        f"{record['temp']:>9.1f} "
        f"{record['humidity']:>8}% "
        f"{record['wind_speed']:>5.1f}  "
        f"{record['weather']:<12} "
        f"{ts}"
    )


def run_once(output_dir: str) -> int:
    """Fetch all cities once. Returns how many succeeded."""
    print_header()
    saved = 0
    for city in config.CITIES:
        record = fetch_weather(city)
        if record:
            print_row(record)
            save_record(record, output_dir)
            saved += 1
    print("-" * 78)
    print(f"Saved {saved}/{len(config.CITIES)} readings to '{output_dir}/'")
    return saved


def main() -> None:
    parser = argparse.ArgumentParser(description="Local weather pipeline (no AWS).")
    parser.add_argument("--once", action="store_true", help="Run a single pass and exit.")
    parser.add_argument("--output", default=config.OUTPUT_DIR, help="Folder for JSON output.")
    args = parser.parse_args()

    if not config.OWM_API_KEY:
        print("[FATAL] OWM_API_KEY is not set. Copy setup.env.example to setup.env "
              "and add your OpenWeatherMap API key.")
        return

    if args.once:
        run_once(args.output)
        return

    print("Weather pipeline started (local mode). Press Ctrl-C to stop.")
    try:
        while True:
            run_once(args.output)
            time.sleep(config.POLL_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
