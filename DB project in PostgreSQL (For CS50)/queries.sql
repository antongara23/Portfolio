-- Find all engines of a particular airline with status 'storage'
SELECT "eng_serial_number", "eng_status" FROM "engines"
JOIN "airlines" ON "airlines"."id" = "engines"."airline_id"
WHERE "airlines"."name" = 'CS50Airways';

-- Find all aircraft which has less than 50 flights cycles till the next maintenance
SELECT "reg_num", "ac_type", "next_check_fc" - "ac_flight_cycles" as "remaining_fc" FROM "aircraft"
WHERE "next_check_fc" - "ac_flight_cycles" <= 50
ORDER BY "next_check_fc" - "ac_flight_cycles" ASC;

-- Find 10 lastest maintenance records of a particular aircraft
SELECT "designation", "date_completion", "fc_record", "fh_record" FROM "maintenance_records"
JOIN "aircraft" ON "aircraft"."id" = "maintenance_records"."ac_id"
JOIN "maintenance_checks" ON "maintenance_checks"."id" = "maintenance_records"."check_id"
WHERE "aircraft"."reg_num" = 'FR-7340'
ORDER BY "maintenance_records"."date_completion" DESC
LIMIT 10;

-- Add a new aircraft
INSERT INTO "aircraft" ("ac_serial_number", "reg_num", "airline_id", "ac_type", "ac_flight_cycles", "next_check_fc", "ac_flight_hours", "next_check_fh", "amp_id")
VALUES
('SN11111', 'US-1111',
	(SELECT "id" FROM "airlines" WHERE "name" = 'CS50Airways'),
	'B737', 0, 500, 0, NULL, 1);

-- Add a new maintenance record
INSERT INTO "maintenance_records" (ac_id , check_id, date_completion, "fc_record", "fh_record")
VALUES (34, 3, '2024-11-21', '1000', '3200');

-- Update engine status
UPDATE "engines" SET "eng_status" = 'storage'
WHERE "id" = (
	SELECT "id" FROM "engines"
	WHERE "eng_serial_number" = 'ESN41453'
);