import os

from dotenv import load_dotenv


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

MTC_API_URL = os.getenv("MTC_API_URL")


if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing")

if not MTC_API_URL:
    raise RuntimeError("MTC_API_URL is missing")


# How much before trip_end_time we start looking for the next trip.
TRIP_END_SAFETY_MINUTES = 5

# Retry interval when the API does not return a new trip.
DISCOVERY_RETRY_SECONDS = 120

# API timeout.
API_TIMEOUT_SECONDS = 15