from supabase import create_client

from config import SUPABASE_URL, SUPABASE_KEY


class Database:

    def __init__(self):

        self.client = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    # =========================================================
    # BUS
    # =========================================================

    def upsert_bus(self, trip: dict):

        data = {
            "vehicle_id": trip["vehicle_id"],
            "bus_no": trip["bus_no"],
            "vehicle_reg_no": trip["vehicle_reg_no"],
            "device_unique_id": trip["device_unique_id"],
            "active": True
        }

        result = (
            self.client
            .table("buses")
            .upsert(
                data,
                on_conflict="vehicle_id"
            )
            .execute()
        )

        return result.data[0]

    # =========================================================
    # ROUTE
    # =========================================================

    def upsert_route(self, trip: dict):

        data = {
            "source_route_id": trip["route_id"],
            "route_no": trip["route_no"],
            "route_name": trip["route_name"],

            "source_station_id":
                trip["source_station_id"],

            "source_station_name":
                trip["source_station_name"],

            "destination_station_id":
                trip["destination_station_id"],

            "destination_station_name":
                trip["destination_station_name"],

            "service_type":
                trip["service_type"],

            "service_type_id":
                trip["service_type_id"]
        }

        result = (
            self.client
            .table("routes")
            .upsert(
                data,
                on_conflict="source_route_id"
            )
            .execute()
        )

        return result.data[0]

    # =========================================================
    # ROUTE STOPS
    # =========================================================

    def upsert_route_stops(
        self,
        route_db_id: int,
        stops: list
    ):

        rows = []

        for stop in stops:

            rows.append({
                "route_id": route_db_id,

                "station_id":
                    stop["station_id"],

                "station_name":
                    stop["station_name"],

                "stop_sequence":
                    stop["stop_sequence"],

                "latitude":
                    stop["latitude"],

                "longitude":
                    stop["longitude"]
            })

        if not rows:
            return []

        result = (
            self.client
            .table("route_stops")
            .upsert(
                rows,
                on_conflict=(
                    "route_id,"
                    "station_id,"
                    "stop_sequence"
                )
            )
            .execute()
        )

        return result.data

    # =========================================================
    # FIND EXISTING TRIP
    # =========================================================

    def get_scheduled_trip(
        self,
        service_date: str,
        source_trip_id: int
    ):

        result = (
            self.client
            .table("scheduled_trips")
            .select("*")
            .eq(
                "service_date",
                service_date
            )
            .eq(
                "source_trip_id",
                source_trip_id
            )
            .limit(1)
            .execute()
        )

        if result.data:
            return result.data[0]

        return None

    # =========================================================
    # CREATE SCHEDULED TRIP
    # =========================================================

    def create_scheduled_trip(
        self,
        trip: dict,
        service_date: str,
        bus_db_id: int,
        route_db_id: int
    ):

        data = {

            "service_date":
                service_date,

            "source_trip_id":
                trip["source_trip_id"],

            "vehicle_id":
                bus_db_id,

            "route_id":
                route_db_id,

            "bus_no":
                trip["bus_no"],

            "source_station_id":
                trip["source_station_id"],

            "destination_station_id":
                trip["destination_station_id"],

            "scheduled_departure_time":
                trip["trip_start_time"],

            "scheduled_arrival_time":
                trip["trip_end_time"],

            "trip_start_time":
                trip["trip_start_time"],

            "trip_end_time":
                trip["trip_end_time"],

            "status":
                "captured"
        }

        result = (
            self.client
            .table("scheduled_trips")
            .insert(data)
            .execute()
        )

        return result.data[0]

    # =========================================================
    # CREATE STOP SCHEDULES
    # =========================================================

    def create_trip_stop_schedules(
        self,
        scheduled_trip_db_id: int,
        stops: list
    ):

        rows = []

        for stop in stops:

            rows.append({

                "scheduled_trip_id":
                    scheduled_trip_db_id,

                "station_id":
                    stop["station_id"],

                "station_name":
                    stop["station_name"],

                "stop_sequence":
                    stop["stop_sequence"],

                "scheduled_arrival_time":
                    stop["scheduled_arrival_time"],

                "scheduled_departure_time":
                    stop["scheduled_departure_time"]
            })

        if not rows:
            return []

        result = (
            self.client
            .table("trip_stop_schedules")
            .insert(rows)
            .execute()
        )

        return result.data