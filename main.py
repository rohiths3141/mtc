from collector import VehicleCollector


# ============================================================
# 10 VEHICLES TO TEST
# ============================================================
#
# IMPORTANT:
# Replace these example IDs with 10 REAL vehicle IDs
# that you want to monitor.
#
# 4087 is confirmed to work from our previous test.
#
# ============================================================

VEHICLE_IDS = [
    4087,
    5326,
    5640,
    4443,
    5357,
    7028,
    6980,
    7036,
    6312,
    5317,
]


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("MTC 10-BUS COLLECTOR TEST")
    print("=" * 70)

    print()
    print(f"Vehicles to process: {len(VEHICLE_IDS)}")

    print()
    print("Vehicle IDs:")
    
    for vehicle_id in VEHICLE_IDS:
        print(f"  - {vehicle_id}")

    print()

    # ========================================================
    # CREATE COLLECTOR
    # ========================================================

    collector = VehicleCollector()

    results = []

    # ========================================================
    # PROCESS EACH VEHICLE
    # ========================================================

    for number, vehicle_id in enumerate(
        VEHICLE_IDS,
        start=1
    ):

        print()
        print(
            f"[{number}/{len(VEHICLE_IDS)}] "
            f"Starting vehicle {vehicle_id}"
        )

        result = collector.collect_vehicle(
            vehicle_id
        )

        results.append(result)

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print()
    print("=" * 70)
    print("10-BUS TEST SUMMARY")
    print("=" * 70)

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    successful = 0
    failed = 0

    new_trips = 0
    existing_trips = 0

    total_stops = 0

    # ========================================================
    # RESULT TABLE
    # ========================================================

    print()

    print(
        f"{'STATUS':<10}"
        f"{'VEHICLE':<12}"
        f"{'BUS':<12}"
        f"{'ROUTE':<12}"
        f"{'TRIP ID':<18}"
        f"{'STOPS':<8}"
    )

    print("-" * 70)

    for result in results:

        # ----------------------------------------------------
        # Success / failure
        # ----------------------------------------------------

        if result["success"]:

            successful += 1

            status = "OK"

        else:

            failed += 1

            status = "FAILED"

        # ----------------------------------------------------
        # New / existing trip
        # ----------------------------------------------------

        if result["new_trip"]:

            new_trips += 1

        else:

            existing_trips += 1

        # ----------------------------------------------------
        # Stops
        # ----------------------------------------------------

        total_stops += result["stops"]

        # ----------------------------------------------------
        # Print result
        # ----------------------------------------------------

        print(
            f"{status:<10}"
            f"{str(result['vehicle_id']):<12}"
            f"{str(result['bus_no'] or '-'): <12}"
            f"{str(result['route_no'] or '-'): <12}"
            f"{str(result['trip_id'] or '-'): <18}"
            f"{str(result['stops']):<8}"
        )

        # ----------------------------------------------------
        # Error
        # ----------------------------------------------------

        if result["error"]:

            print(
                f"           ERROR: "
                f"{result['error']}"
            )

    # ========================================================
    # FINAL STATISTICS
    # ========================================================

    print()
    print("-" * 70)

    print(
        f"Total vehicles processed : "
        f"{len(VEHICLE_IDS)}"
    )

    print(
        f"Successful requests      : "
        f"{successful}"
    )

    print(
        f"Failed requests          : "
        f"{failed}"
    )

    print(
        f"New trips captured       : "
        f"{new_trips}"
    )

    print(
        f"Existing trips           : "
        f"{existing_trips}"
    )

    print(
        f"Total stops processed    : "
        f"{total_stops}"
    )

    print("=" * 70)

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    if failed == 0:

        print()
        print(
            "10-BUS TEST COMPLETED SUCCESSFULLY."
        )

    else:

        print()
        print(
            f"10-BUS TEST COMPLETED WITH "
            f"{failed} FAILED VEHICLE(S)."
        )

    print()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()