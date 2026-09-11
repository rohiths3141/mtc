-- =========================================================
-- BUSES
-- =========================================================

create table if not exists buses (
    id bigint generated always as identity primary key,

    vehicle_id bigint not null unique,

    bus_no text,
    vehicle_reg_no text,
    device_unique_id text,

    active boolean not null default true,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);


-- =========================================================
-- ROUTES
-- =========================================================

create table if not exists routes (
    id bigint generated always as identity primary key,

    source_route_id bigint not null unique,

    route_no text,
    route_name text,

    source_station_id bigint,
    source_station_name text,

    destination_station_id bigint,
    destination_station_name text,

    service_type text,
    service_type_id bigint,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);


-- =========================================================
-- ROUTE STOPS
-- =========================================================

create table if not exists route_stops (
    id bigint generated always as identity primary key,

    route_id bigint not null references routes(id)
        on delete cascade,

    station_id bigint not null,
    station_name text,

    stop_sequence integer,

    latitude double precision,
    longitude double precision,

    created_at timestamptz not null default now(),

    unique(route_id, station_id, stop_sequence)
);


create index if not exists idx_route_stops_route
on route_stops(route_id);


-- =========================================================
-- SCHEDULED TRIPS
-- =========================================================

create table if not exists scheduled_trips (
    id bigint generated always as identity primary key,

    source_trip_id bigint not null,

    vehicle_id bigint references buses(id),

    route_id bigint references routes(id),

    bus_no text,

    source_station_id bigint,
    destination_station_id bigint,

    scheduled_departure_time time,
    scheduled_arrival_time time,

    trip_start_time time,
    trip_end_time time,

    captured_at timestamptz not null default now(),

    status text not null default 'captured',

    unique(source_trip_id)
);


create index if not exists idx_scheduled_trips_vehicle
on scheduled_trips(vehicle_id);


create index if not exists idx_scheduled_trips_route
on scheduled_trips(route_id);


create index if not exists idx_scheduled_trips_end
on scheduled_trips(trip_end_time);


-- =========================================================
-- TRIP STOP SCHEDULES
-- =========================================================

create table if not exists trip_stop_schedules (
    id bigint generated always as identity primary key,

    scheduled_trip_id bigint not null
        references scheduled_trips(id)
        on delete cascade,

    station_id bigint not null,

    station_name text,

    stop_sequence integer,

    scheduled_arrival_time time,
    scheduled_departure_time time,

    created_at timestamptz not null default now(),

    unique(scheduled_trip_id, station_id, stop_sequence)
);


create index if not exists idx_trip_stop_schedule_trip
on trip_stop_schedules(scheduled_trip_id);


create index if not exists idx_trip_stop_schedule_station
on trip_stop_schedules(station_id);


-- =========================================================
-- LIVE TRIPS
-- =========================================================

create table if not exists live_trips (
    id bigint generated always as identity primary key,

    vehicle_id bigint not null
        references buses(id)
        on delete cascade,

    source_trip_id bigint,

    route_id bigint
        references routes(id)
        on delete set null,

    bus_no text,

    current_stop_id bigint,
    current_stop_name text,

    last_stop_id bigint,
    last_stop_name text,

    next_stop_id bigint,
    next_stop_name text,

    latitude double precision,
    longitude double precision,

    eta time,

    actual_arrival_time time,
    actual_departure_time time,

    trip_status text,

    crowd integer,
    heading double precision,

    last_api_update timestamptz,

    updated_at timestamptz not null default now(),

    unique(vehicle_id)
);


-- =========================================================
-- ACTUAL STOP EVENTS
-- =========================================================

create table if not exists actual_stop_events (
    id bigint generated always as identity primary key,

    scheduled_trip_id bigint
        references scheduled_trips(id)
        on delete set null,

    vehicle_id bigint
        references buses(id)
        on delete set null,

    source_trip_id bigint,

    station_id bigint,
    station_name text,

    actual_arrival_time time,
    actual_departure_time time,

    latitude double precision,
    longitude double precision,

    captured_at timestamptz not null default now()
);


create index if not exists idx_actual_stop_events_trip
on actual_stop_events(source_trip_id);


create index if not exists idx_actual_stop_events_station
on actual_stop_events(station_id);


-- =========================================================
-- COLLECTOR STATE
-- =========================================================

create table if not exists collector_state (
    id bigint generated always as identity primary key,

    vehicle_id bigint not null
        references buses(id)
        on delete cascade,

    state text not null default 'unknown',

    current_source_trip_id bigint,

    current_scheduled_trip_id bigint
        references scheduled_trips(id)
        on delete set null,

    trip_start_time time,
    trip_end_time time,

    next_poll_at timestamptz,

    last_success_at timestamptz,
    last_error_at timestamptz,

    consecutive_errors integer not null default 0,

    updated_at timestamptz not null default now(),

    unique(vehicle_id)
);


create index if not exists idx_collector_next_poll
on collector_state(next_poll_at);