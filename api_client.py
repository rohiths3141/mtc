import json
import requests

from config import MTC_API_URL, API_TIMEOUT_SECONDS


class MTCAPIClient:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        })

    def get_vehicle_trip_details(
        self,
        vehicle_id: int
    ) -> dict:

        payload = {
            "vehicleId": vehicle_id
        }

        response = self.session.post(
            MTC_API_URL,
            json=payload,
            timeout=API_TIMEOUT_SECONDS
        )

        response.raise_for_status()

        # First JSON decoding
        data = response.json()

        # -----------------------------------------------------
        # MTC API may return JSON encoded as a string.
        #
        # Example:
        #
        # response.json()
        #
        # returns:
        #
        # '{"RouteDetails":[...]}'
        #
        # instead of:
        #
        # {"RouteDetails":[...]}
        # -----------------------------------------------------

        if isinstance(data, str):

            data = json.loads(data)

        # -----------------------------------------------------
        # Final validation
        # -----------------------------------------------------

        if not isinstance(data, dict):

            raise ValueError(
                f"Unexpected API response type: {type(data).__name__}"
            )

        if "RouteDetails" not in data:

            raise ValueError(
                "API response does not contain 'RouteDetails'"
            )

        return data