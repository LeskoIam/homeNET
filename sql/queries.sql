SELECT DSD.date_time, DSD.value_diff, DSD.time_diff, (DSD.value_diff/DSD.time_diff) AS cons
FROM diff_sensor_data as DSD
WHERE DSD.sensor_id = 3
ORDER BY DSD.date_time DESC ;


SELECT count(*)
FROM sensor_data as sd
WHERE sensor_id = 1
AND sd.date_time BETWEEN '2015-12-26 00:00:00' AND '2015-12-27 00:00:00';


-- All heating sensors
SELECT sen.id, sen.location, sen.sensor_type
FROM sensors as sen
WHERE sen.sensor_type = 'heat consumption';

-- All water sensors
SELECT sen.id, sen.location, sen.sensor_type
FROM sensors as sen
WHERE sen.sensor_type LIKE '% water consumption';


-- SUM consumption
-- Get sum heat consumption [e/hr]
SELECT D_SD.date_time, sum((D_SD.value_diff/D_SD.time_diff)*60*60)
FROM diff_sensor_data AS D_SD
WHERE D_SD.sensor_id IN (2, 3, 4, 5)
GROUP BY D_SD.date_time
  ORDER BY D_SD.date_time DESC
LIMIT 100;

-- Get sum water consumption [l/hr]
SELECT D_SD.date_time, sum((D_SD.value_diff/D_SD.time_diff)*60*60*1000)
FROM diff_sensor_data AS D_SD
WHERE D_SD.sensor_id IN (6, 7)
GROUP BY D_SD.date_time
  ORDER BY D_SD.date_time DESC
LIMIT 100;


-- PER NODE consumption
-- Get heating consumption [e/hr]
SELECT
  D_SD.sensor_id,
  D_SD.date_time,
  D_SD.value_diff,
  D_SD.time_diff,
  (D_SD.value_diff/D_SD.time_diff)*60*60
FROM diff_sensor_data AS D_SD
WHERE D_SD.sensor_id IN (2, 3, 4, 5)
ORDER BY D_SD.date_time DESC;

-- Get water consumption [l/hr]
SELECT
  D_SD.sensor_id,
  D_SD.date_time,
  D_SD.value_diff,
  D_SD.time_diff,
  (D_SD.value_diff/D_SD.time_diff)*60*60*1000
FROM diff_sensor_data AS D_SD
WHERE D_SD.sensor_id IN (6, 7)
ORDER BY D_SD.date_time DESC;


-- JOINT the two queries
SELECT D_SD.date_time, sum((D_SD.value_diff/D_SD.time_diff)*60*60)
FROM diff_sensor_data AS D_SD, sensors as sen
WHERE sen.id = D_SD.sensor_id
      AND sen.sensor_type = 'heat consumption'
GROUP BY D_SD.date_time
ORDER BY D_SD.date_time DESC
LIMIT 100;


-- maximum reading per sensor
SELECT
  sen.id,
  sen.location,
  sen.sensor_type,
  min(sd.value) AS min_value,
  max(sd.value) AS max_value
FROM sensor_data AS sd, sensors as sen
WHERE sd.sensor_id = sen.id
GROUP BY sen.id
ORDER BY sen.id
