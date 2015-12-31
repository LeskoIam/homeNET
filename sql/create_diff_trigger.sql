-- Create diff table

-- CREATE TABLE diff_sensor_data
-- (
--   id serial NOT NULL,
--   sensor_id integer,
--   date_time timestamp without time zone NOT NULL,
--   value_diff double precision NOT NULL,
--   time_diff double precision NOT NULL,
--   unique (sensor_id, date_time),
--   CONSTRAINT diff_sensor_data_pkey PRIMARY KEY (id),
--   CONSTRAINT diff_sensor_data_sensor_id_fkey FOREIGN KEY (sensor_id)
--       REFERENCES sensors (id) MATCH SIMPLE
--       ON UPDATE NO ACTION ON DELETE NO ACTION
-- )
-- WITH (
--   OIDS=FALSE
-- );
-- ALTER TABLE diff_sensor_data
--   OWNER TO lesko;



-- Create function to calculate diff
CREATE OR REPLACE FUNCTION my_diff_func()
  RETURNS trigger AS
$BODY$
DECLARE
    old_value double precision;
    old_time timestamp without time zone;
    time_diff double precision;
    value_diff double precision;
BEGIN
    IF (TG_TABLE_NAME = 'sensor_data') THEN
        --RAISE NOTICE 'TRIGGER called on %', TG_TABLE_NAME;

    SELECT sensor_data.value, sensor_data.date_time
    INTO old_value, old_time
    FROM sensor_data
     WHERE sensor_data.sensor_id = NEW.sensor_id
    ORDER BY sensor_data.date_time DESC LIMIT 1;

    value_diff := NEW.value - old_value;
    time_diff := EXTRACT(EPOCH FROM (NEW.date_time - old_time));

    --RAISE NOTICE 'test me too %', value_diff;
    --RAISE NOTICE 'date %', time_diff;

    IF (SELECT EXISTS(
          SELECT 1
          FROM sensor_data
          WHERE sensor_data.sensor_id = NEW.sensor_id)
    ) THEN
    INSERT INTO diff_sensor_data(sensor_id, date_time, value_diff, time_diff)
            VALUES(NEW.sensor_id, NEW.date_time, value_diff, time_diff);
    END IF;

    END IF;


    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


-- Register function to table
-- CREATE TRIGGER my_diff_func_trigger
-- BEFORE INSERT
-- ON sensor_data
-- FOR EACH ROW
-- EXECUTE PROCEDURE my_diff_func();