INSERT INTO "airlines" ("name", "registration_state", "arl_status", "date_established", "date_closed")
VALUES
    ('CS50Airways', 'US', 'active', '2001-01-01', NULL),
    ('LondonSky', 'GB', 'active', '1995-05-15', NULL),
    ('AirAmerica', 'US', 'active', '1991-02-01', NULL),
    ('WestFlights', 'US', 'closed', '1980-01-01', '2001-01-05'),
    ('Aeroplan', 'RU', 'active', '2010-02-03', NULL),
    ('FrenchSky', 'FR', 'active', '2000-01-01', NULL),
    ('TransAmerica', 'US', 'active', '1960-01-01', NULL),
   	('OneMoreFlight', 'US', 'active', '1988-01-01', NULL);

INSERT INTO "maintenance_program" ("identifier", "revision", "revision_date")
VALUES
	('AMP-B-737-0001-2022', '12', '2022-05-01'),
	('AMP-A-320-MN12-2023', '16', '2023-08-01')
;

INSERT INTO "maintenance_checks" ("amp_id", "designation", "interval_fc", "interval_fh")
VALUES
	(1, 'A1', 100, 400),
	(1, 'A4', 200, 800),
	(1, 'C1', 600, 1200),
	(1, 'C2', 1200, 2400),
	(2, 'B1', 500, 500),
	(2, 'B2', 400, 1000)
;