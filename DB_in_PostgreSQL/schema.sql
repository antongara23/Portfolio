-- Custom types
CREATE TYPE "country_code" AS ENUM ('US', 'GB', 'FR', 'RU');
CREATE TYPE "aircraft_type" AS ENUM ('B737', 'A320');
CREATE TYPE "component_status" AS ENUM ('storage', 'installed', 'overhaul');
CREATE TYPE "engine_type" AS ENUM ('CFM56-3', 'CFM56-5', 'CFM56-7');

-- Represent airline companies
CREATE TABLE IF NOT EXISTS  "airlines" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(64) NOT NULL UNIQUE,
    "registration_state" country_code NOT NULL,
    "arl_status" VARCHAR(6) NOT NULL CHECK ("arl_status" IN ('active', 'closed')),
    "date_established" DATE NOT NULL CHECK ("date_established" <= CURRENT_DATE),
    "date_closed" DATE DEFAULT NULL CHECK ("date_closed" IS NULL OR ("date_closed" > "date_established" AND "date_closed" <= CURRENT_DATE)),
    CONSTRAINT "check_arl_status" CHECK ("arl_status" = 'closed' OR "date_closed" IS NULL)
);

-- Represent Aircraft Maintenance Program (AMP)
CREATE TABLE IF NOT EXISTS "maintenance_program" (
	"id" SERIAL PRIMARY KEY,
	"identifier" VARCHAR(128) NOT NULL UNIQUE,
	"revision" VARCHAR(4) NOT NULL,
	"revision_date" DATE NOT NULL CHECK ("revision_date" <= CURRENT_DATE)
);

-- Represent aircraft
CREATE TABLE IF NOT EXISTS "aircraft" (
	"id" SERIAL PRIMARY KEY,
    "ac_serial_number" VARCHAR(16) NOT NULL UNIQUE,
    "reg_num" VARCHAR(16) UNIQUE,
    "airline_id" INTEGER NOT NULL,
    "ac_type" aircraft_type NOT NULL,
    "ac_flight_cycles" INTEGER NOT NULL,
    "next_check_fc" INTEGER,
    "ac_flight_hours" NUMERIC(10, 1) NOT NULL,
    "next_check_fh" NUMERIC(10, 1),
    "amp_id" INTEGER,
    CONSTRAINT "check_next_check" CHECK ("next_check_fc" IS NOT NULL OR "next_check_fh" IS NOT NULL),
    CONSTRAINT "check_positive" CHECK ("ac_flight_cycles" >= 0 AND "next_check_fc" >= 0 AND "ac_flight_hours" >= 0 AND "next_check_fh" >= 0),
    FOREIGN KEY ("airline_id") REFERENCES "airlines"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("amp_id") REFERENCES "maintenance_program"("id") ON DELETE SET NULL
);

-- Represent aircraft engine
CREATE TABLE IF NOT EXISTS "engines" (
	"id" SERIAL PRIMARY KEY,
    "eng_serial_number" VARCHAR(16) NOT NULL UNIQUE,
    "airline_id" INTEGER NOT NULL,
    "ac_id" INTEGER,
    "eng_type" engine_type NOT NULL,
    "eng_flight_cycles" INTEGER NOT NULL,
    "last_overhaul_fc" INTEGER CHECK ("last_overhaul_fc" <= "eng_flight_cycles"),
    "last_overhaul_date" DATE,
    "eng_status" component_status NOT NULL,
    FOREIGN KEY ("airline_id") REFERENCES "airlines"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("ac_id") REFERENCES "aircraft"("id") ON DELETE SET NULL
);

-- Represent package of tasks having a particular interval
CREATE TABLE IF NOT EXISTS "maintenance_checks" (
	"id" SERIAL PRIMARY KEY,
	"amp_id" INTEGER NOT NULL,
	"designation" VARCHAR(16) NOT NULL,
	"interval_fc" INTEGER CHECK ("interval_fc" > 0),
	"interval_fh" INTEGER CHECK ("interval_fh" > 0),
	FOREIGN KEY ("amp_id") REFERENCES "maintenance_program"("id") ON DELETE SET NULL,
	CONSTRAINT "unique_check_per_amp" UNIQUE ("amp_id", "designation"),
	CONSTRAINT "unique_interval" UNIQUE ("amp_id", "interval_fc", "interval_fh"),
	CONSTRAINT "interval_check" CHECK ("interval_fc" IS NOT NULL OR "interval_fh" IS NOT NULL)
);

-- Represent technical records of completed maintenance on the aircraft
CREATE TABLE IF NOT EXISTS "maintenance_records" (
	"id" SERIAL PRIMARY KEY,
	"ac_id" INTEGER NOT NULL,
	"check_id" INTEGER NOT NULL,
	"date_completion" DATE NOT NULL CHECK ("date_completion" <= CURRENT_DATE),
	"fc_record" INTEGER NOT NULL,
	"fh_record" NUMERIC(10, 1) NOT
	NULL,
	FOREIGN KEY ("ac_id") REFERENCES "aircraft" ("id") ON DELETE RESTRICT,
	FOREIGN KEY ("check_id") REFERENCES "maintenance_checks" ("id") ON DELETE RESTRICT,
	CONSTRAINT "record_check" CHECK ("fc_record" > 0 AND "fh_record" > 0)
);

CREATE INDEX "aircraft_search" ON "aircraft" ("reg_num");
CREATE INDEX "engine_search" ON "engines" ("eng_serial_number");
CREATE INDEX "records_search" ON "maintenance_records" ("ac_id");