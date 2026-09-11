import traceback
from datetime import datetime

from api_client import MTCAPIClient
from parser import parse_vehicle_response
from database import Database


class VehicleCollector:

    def __init__(self):

        # ========================================================
        # API CLIENT
        # ========================================================

        self.api_client = MTCAPIClient()

        # ========================================================
        # DATABASE
        # ========================================================

        self.db = Database()

    # ============================================================
    # GET SERVICE DATE
    # ============================================================

    def get_service_date(self):

        return datetime.now().strftime("%Y-%m-%d")

    # ============================================================
    # COLLECT ONE VEHICLE
    # ============================================================

    def collect_vehicle(self, vehicle_id):

        print()
        print("=" * 70)
        print(
            f"PROCESSING VEHICLE: {vehicle_id}"
        )
        print("=" * 70)

        result = {
            "vehicle_id": vehicle_id,
            "success": False,
            "status": "UNKNOWN",
            "new_trip": False,
            "trip_id": None,
            "bus_no": None,
            "route_no": None,
            "stops": 0,
            "error": None,
        }

        try:

            # ====================================================
            # 1. REQUEST MTC API
            # ====================================================

            print("Requesting MTC API...")

            response = (
                self.api_client
                .get_vehicle_trip_details(
                    vehicle_id
                )
            )

            print("API request successful.")

            # ====================================================
            # 2. PARSE RESPONSE
            # ====================================================

            trip = parse_vehicle_response(
                response
            )

            if not isinstance(trip, dict):

                raise ValueError(
                    "Parser returned invalid result"
                )

            status = trip.get(
                "status"
            )

            # ====================================================
            # 3. OFFLINE
            # ====================================================

            if status == "OFFLINE":

                print()
                print("BUS OFFLINE")
                print("-" * 70)

                print(
                    f"Vehicle ID : "
                    f"{trip.get('vehicle_id')}"
                )

                print(
                    f"Bus Number : "
                    f"{trip.get('bus_no')}"
                )

                print(
                    f"Location   : "
                    f"{trip.get('location')}"
                )

                print(
                    f"Latitude   : "
                    f"{trip.get('latitude')}"
                )

                print(
                    f"Longitude  : "
                    f"{trip.get('longitude')}"
                )

                print(
                    f"Status     : "
                    f"{trip.get('last_refresh')}"
                )

                result["success"] = True
                result["status"] = "OFFLINE"
                result["bus_no"] = trip.get(
                    "bus_no"
                )

                return result

            # ====================================================
            # 4. NO DATA
            # ====================================================

            if status == "NO_DATA":

                print()
                print("NO ACTIVE TRIP")
                print("-" * 70)

                if trip.get("vehicle_id"):

                    print(
                        f"Vehicle ID : "
                        f"{trip.get('vehicle_id')}"
                    )

                if trip.get("bus_no"):

                    print(
                        f"Bus Number : "
                        f"{trip.get('bus_no')}"
                    )

                if trip.get("location"):

                    print(
                        f"Location   : "
                        f"{trip.get('location')}"
                    )

                if trip.get("last_refresh"):

                    print(
                        f"Status     : "
                        f"{trip.get('last_refresh')}"
                    )

                result["success"] = True
                result["status"] = "NO_DATA"
                result["bus_no"] = trip.get(
                    "bus_no"
                )

                return result

            # ====================================================
            # 5. ACTIVE TRIP
            # ====================================================

            if status != "ACTIVE":

                raise ValueError(
                    f"Unknown parser status: {status}"
                )

            # ====================================================
            # 6. ACTIVE TRIP INFORMATION
            # ====================================================

            stops = trip.get(
                "stops",
                []
            )

            result["status"] = "ACTIVE"

            result["bus_no"] = trip.get(
                "bus_no"
            )

            result["route_no"] = trip.get(
                "route_no"
            )

            result["trip_id"] = trip.get(
                "source_trip_id"
            )

            result["stops"] = len(
                stops
            )

            print()
            print("Trip detected:")
            print(
                f"  Bus       : "
                f"{trip.get('bus_no')}"
            )

            print(
                f"  Route     : "
                f"{trip.get('route_no')}"
            )

            print(
                f"  Route ID  : "
                f"{trip.get('route_id')}"
            )

            print(
                f"  Trip ID   : "
                f"{trip.get('source_trip_id')}"
            )

            print(
                f"  Start     : "
                f"{trip.get('trip_start_time')}"
            )

            print(
                f"  End       : "
                f"{trip.get('trip_end_time')}"
            )

            print(
                f"  Source    : "
                f"{trip.get('source_station_name')}"
            )

            print(
                f"  Destination: "
                f"{trip.get('destination_station_name')}"
            )

            print(
                f"  Stops     : "
                f"{len(stops)}"
            )

            # ====================================================
            # 7. SAVE / UPDATE BUS
            # ====================================================

            bus = self.db.upsert_bus(
                trip
            )

            print(
                f"Bus saved/updated. "
                f"DB ID: {bus['id']}"
            )

            # ====================================================
            # 8. SAVE / UPDATE ROUTE
            # ====================================================

            route = self.db.upsert_route(
                trip
            )

            print(
                f"Route saved/updated. "
                f"DB ID: {route['id']}"
            )

            # ====================================================
            # 9. SAVE / UPDATE ROUTE STOPS
            # ====================================================

            route_stops = (
                self.db.upsert_route_stops(
                    route_db_id=route["id"],
                    stops=stops
                )
            )

            print(
                f"Route stops saved/updated: "
                f"{len(route_stops)}"
            )

            # ====================================================
            # 10. SERVICE DATE
            # ====================================================

            service_date = (
                trip.get("service_date")
                or self.get_service_date()
            )

            # ====================================================
            # 11. CHECK EXISTING TRIP
            # ====================================================

            existing_trip = (
                self.db.get_scheduled_trip(
                    service_date=service_date,
                    source_trip_id=trip[
                        "source_trip_id"
                    ]
                )
            )

            # ====================================================
            # 12. EXISTING TRIP
            # ====================================================

            if existing_trip:

                print()
                print("EXISTING TRIP")

                print(
                    f"Database Trip ID: "
                    f"{existing_trip['id']}"
                )

                print(
                    "Schedule capture skipped."
                )

                result["success"] = True

                return result

            # ====================================================
            # 13. NEW TRIP
            # ====================================================

            print()
            print("NEW TRIP FOUND!")

            print(
                "Capturing schedule..."
            )

            scheduled_trip = (
                self.db.create_scheduled_trip(
                    trip=trip,
                    service_date=service_date,
                    bus_db_id=bus["id"],
                    route_db_id=route["id"]
                )
            )

            print(
                f"Scheduled trip saved: "
                f"{scheduled_trip['id']}"
            )

            result["new_trip"] = True

            # ====================================================
            # 14. SAVE ALL STOP SCHEDULES ONCE
            # ====================================================

            stop_schedules = (
                self.db.create_trip_stop_schedules(
                    scheduled_trip_db_id=
                        scheduled_trip["id"],
                    stops=stops
                )
            )

            print(
                f"Stop schedules saved: "
                f"{len(stop_schedules)}"
            )

            # ====================================================
            # 15. SUCCESS
            # ====================================================

            result["success"] = True

            return result

        # ========================================================
        # ACTUAL ERROR
        # ========================================================

        except Exception as e:

            result["success"] = False
            result["status"] = "ERROR"
            result["error"] = str(e)

            print()
            print("=" * 70)
            print("ERROR PROCESSING VEHICLE")
            print("=" * 70)

            print(
                f"Vehicle ID: {vehicle_id}"
            )

            print(
                f"Error: {e}"
            )

            traceback.print_exc()

            return result