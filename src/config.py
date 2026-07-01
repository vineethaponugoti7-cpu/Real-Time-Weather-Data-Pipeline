"""
Configuration for the weather pipeline.

All secrets (API keys, AWS details) are read from environment variables,
loaded from a local `setup.env` file that is NEVER committed to git.
See setup.env.example for the variables you need to set.
"""

import os

from dotenv import load_dotenv

# Load environment variables from setup.env if it exists.
load_dotenv("setup.env")

# ---- OpenWeatherMap ----
OWM_API_KEY = os.getenv("OWM_API_KEY")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---- AWS / Kinesis (only needed for the cloud version) ----
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
KINESIS_STREAM = os.getenv("KINESIS_STREAM", "weather-stream")

# ---- Producer settings ----
CITIES = [
    "New York", "London", "Tokyo", "Los Angeles", "Chicago",
    "Hyderabad", "Bangalore", "Delhi", "Boston", "Chennai",
    "Berlin", "Madrid", "Sydney", "Toronto", "Singapore",
]

# How often to poll the API, in seconds.
POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", "10"))

# Where local mode writes its JSON output.
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "data")
