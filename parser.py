import json


# ================================================================
# HELPER
# ================================================================

def get_value(data, *keys, default=None):
    """
    Return the first available value from a dictionary.

    This makes the parser tolerant of small differences in
    MTC API field naming.
    """

    if not isinstance(data, dict):
        return default

    for key in keys:

        if key in data:

            value = data[key]

            if value is not None and value != "":
                return value

    return default


# ================================================================
# PARSE VEHICLE RESPONSE
# ================================================================

def parse_vehicle_response(response):
    """
    Parse MTC VehicleTripDetails_v2 response.

    Returns:

        ACTIVE
        OFFLINE
        NO_DATA
    """

    # ============================================================
    # NORMALIZE RESPONSE
    # ============================================================

    if isinstance(response, str):

        try:

            response = json.loads(response)

        except json.JSONDecodeError as e:

            raise ValueError(
                f"Invalid JSON response from MTC API: {e}"
            )

    if not isinstance(response, dict):

        raise ValueError(
            "MTC API response is not a JSON object"
        )

    # ============================================================
    # GET RESPONSE DATA
    # ============================================================

    route_details = response.get(
        "RouteDetails",
        []
    )

    live_location = response.get(
        "LiveLocation",
        []
    )

    # ============================================================
    # ACTIVE BUS
    # ============================================================

    if route_details:

        return parse_active_trip(
            route_details,
            live_location
        )

    # ============================================================
    # NO ROUTE DETAILS
    # ============================================================

    if live_location:

        location_data = live_location[0]

        vehicle_id = get_value(
            location_data,
            "vehicleid",
            "vehicleId",
            "VehicleId"
        )

        bus_no = get_value(
            location_data,
            "vehiclenumber",
            "vehicleNumber",
            "VehicleNumber"
        )

        latitude = get_value(
            location_data,
            "latitude",
            "Latitude"
        )

        longitude = get_value(
            location_data,
            "longitude",
            "Longitude"
        )

        location = get_value(
            location_data,
            "location",
            "Location"
        )

        last_refresh = get_value(
            location_data,
            "lastrefreshon",
            "lastRefreshOn",
            "LastRefreshOn"
        )

        # --------------------------------------------------------
        # OFFLINE
        # --------------------------------------------------------

        if (
            isinstance(last_refresh, str)
            and "offline" in last_refresh.lower()
        ):

            return {
                "status": "OFFLINE",

                "vehicle_id": vehicle_id,

                "bus_no": bus_no,

                "latitude": latitude,

                "longitude": longitude,

                "location": location,

                "last_refresh": last_refresh,

                "live_location": location_data,
            }

        # --------------------------------------------------------
        # NO ACTIVE TRIP
        # --------------------------------------------------------

        return {
            "status": "NO_DATA",

            "vehicle_id": vehicle_id,

            "bus_no": bus_no,

            "latitude": latitude,

            "longitude": longitude,

            "location": location,

            "last_refresh": last_refresh,

            "live_location": location_data,
        }

    # ============================================================
    # COMPLETELY EMPTY
    # ============================================================

    return {
        "status": "NO_DATA",

        "vehicle_id": None,

        "bus_no": None,

        "latitude": None,

        "longitude": None,

        "location": None,

        "last_refresh": None,

        "live_location": None,
    }


# =================================================================
# ACTIVE TRIP
# =================================================================

def parse_active_trip(
    rows,
    live_location=None
):

    if not rows:

        raise ValueError(
            "Cannot parse active trip without RouteDetails"
        )

    # ============================================================
    # FIRST ROUTE RECORD
    # ============================================================

    first = rows[0]

    # ============================================================
    # LIVE LOCATION RECORD
    # ============================================================

    live = {}

    if live_location:

        live = live_location[0]

    # ============================================================
    # VEHICLE ID
    # ============================================================

    vehicle_id = get_value(
        first,
        "vehicleid",
        "vehicleId",
        "VehicleId"
    )

    if vehicle_id is None:

        vehicle_id = get_value(
            live,
            "vehicleid",
            "vehicleId",
            "VehicleId"
        )

    # ============================================================
    # BUS NUMBER
    # ============================================================

    bus_no = get_value(
        first,
        "vehiclenumber",
        "vehicleNumber",
        "VehicleNumber",
        "busno",
        "busNo",
        "BusNo"
    )

    # If RouteDetails doesn't contain it,
    # use LiveLocation.

    if bus_no is None:

        bus_no = get_value(
            live,
            "vehiclenumber",
            "vehicleNumber",
            "VehicleNumber",
            "busno",
            "busNo",
            "BusNo"
        )

    # ============================================================
    # VEHICLE REGISTRATION NUMBER
    # ============================================================

    vehicle_reg_no = get_value(
        first,
        "vehicleregno",
        "vehicleRegNo",
        "VehicleRegNo",
        "vehicleregistrationno",
        "vehicleRegistrationNo",
        "registrationno",
        "registrationNo",
        "regno",
        "regNo"
    )

    # Try LiveLocation if RouteDetails doesn't have it.

    if vehicle_reg_no is None:

        vehicle_reg_no = get_value(
            live,
            "vehicleregno",
            "vehicleRegNo",
            "VehicleRegNo",
            "vehicleregistrationno",
            "vehicleRegistrationNo",
            "registrationno",
            "registrationNo",
            "regno",
            "regNo"
        )

    # ============================================================
    # DEVICE UNIQUE ID
    # ============================================================

    device_unique_id = get_value(
        first,
        "deviceuniqueid",
        "deviceUniqueId",
        "DeviceUniqueId"
    )

    if device_unique_id is None:

        device_unique_id = get_value(
            live,
            "deviceuniqueid",
            "deviceUniqueId",
            "DeviceUniqueId"
        )

    # ============================================================
    # ROUTE
    # ============================================================

    route_id = get_value(
        first,
        "routeid",
        "routeId",
        "RouteId"
    )

    route_no = get_value(
        first,
        "routeno",
        "routeNo",
        "RouteNo"
    )

    route_name = get_value(
        first,
        "routename",
        "routeName",
        "RouteName"
    )

    # ============================================================
    # TRIP ID
    # ============================================================

    source_trip_id = get_value(
        first,
        "tripid",
        "tripId",
        "TripId"
    )

    # ============================================================
    # TRIP START
    # ============================================================

    trip_start_time = get_value(
        first,

        "tripstarttime",
        "tripStartTime",
        "TripStartTime",

        "scheduleddeparturetime",
        "scheduledDepartureTime",
        "ScheduledDepartureTime"
    )

    # ============================================================
    # TRIP END
    # ============================================================

    trip_end_time = get_value(
        first,

        "tripendtime",
        "tripEndTime",
        "TripEndTime",

        "scheduledendtime",
        "scheduledEndTime",
        "ScheduledEndTime"
    )

    # ============================================================
    # SOURCE
    # ============================================================

    source_station_id = get_value(
        first,

        "sourceid",
        "sourceId",
        "SourceId",

        "source_station_id",
        "sourceStationId"
    )

    source_station_name = get_value(
        first,

        "sourcename",
        "sourceName",
        "SourceName",

        "source_station_name",
        "sourceStationName"
    )

    # ============================================================
    # DESTINATION
    # ============================================================

    destination_station_id = get_value(
        first,

        "destinationid",
        "destinationId",
        "DestinationId",

        "destination_station_id",
        "destinationStationId"
    )

    destination_station_name = get_value(
        first,

        "destinationname",
        "destinationName",
        "DestinationName",

        "destination_station_name",
        "destinationStationName"
    )

    # ============================================================
    # SERVICE TYPE
    # ============================================================

    service_type_id = get_value(
        first,

        "servicetypeid",
        "serviceTypeId",
        "ServiceTypeId"
    )

    service_type = get_value(
        first,

        "servicetype",
        "serviceType",
        "ServiceType"
    )

    # ============================================================
    # STOPS
    # ============================================================

    stops = []

    for index, row in enumerate(
        rows,
        start=1
    ):

        station_id = get_value(
            row,

            "stationid",
            "stationId",
            "StationId"
        )

        station_name = get_value(
            row,

            "stationname",
            "stationName",
            "StationName"
        )

        arrival_time = get_value(
            row,

            "scheduledarrivaltime",
            "scheduledArrivalTime",
            "ScheduledArrivalTime",

            "arrivalTime",
            "arrivaltime"
        )

        departure_time = get_value(
            row,

            "scheduleddeparturetime",
            "scheduledDepartureTime",
            "ScheduledDepartureTime",

            "departureTime",
            "departuretime"
        )

        latitude = get_value(
            row,

            "latitude",
            "Latitude"
        )

        longitude = get_value(
            row,

            "longitude",
            "Longitude"
        )

        stops.append(
            {
                "station_id":
                    station_id,

                "station_name":
                    station_name,

                "stop_sequence":
                    index,

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "scheduled_arrival_time":
                    arrival_time,

                "scheduled_departure_time":
                    departure_time,
            }
        )

    # ============================================================
    # SERVICE DATE
    # ============================================================

    service_date = get_value(
        first,

        "servicedate",
        "serviceDate",
        "ServiceDate"
    )

    # ============================================================
    # RETURN ACTIVE TRIP
    # ============================================================

    return {

        "status": "ACTIVE",

        "vehicle_id":
            vehicle_id,

        "bus_no":
            bus_no,

        "vehicle_reg_no":
            vehicle_reg_no,

        "device_unique_id":
            device_unique_id,

        "route_id":
            route_id,

        "route_no":
            route_no,

        "route_name":
            route_name,

        "source_trip_id":
            source_trip_id,

        "service_date":
            service_date,

        "trip_start_time":
            trip_start_time,

        "trip_end_time":
            trip_end_time,

        "source_station_id":
            source_station_id,

        "source_station_name":
            source_station_name,

        "destination_station_id":
            destination_station_id,

        "destination_station_name":
            destination_station_name,

        "service_type_id":
            service_type_id,

        "service_type":
            service_type,

        "stops":
            stops,

        "live_location":
            live if live else None,
    }