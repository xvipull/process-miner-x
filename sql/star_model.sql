-- Canonical SQLite star schema. The pipeline creates this equivalent schema before each rebuild.
-- Grain: one accepted source event in fact_process_event.
CREATE TABLE dim_case (case_key INTEGER PRIMARY KEY, case_id TEXT NOT NULL UNIQUE, product_or_service TEXT, region_or_channel TEXT, customer_id TEXT);
CREATE TABLE dim_activity (activity_key INTEGER PRIMARY KEY, activity_name TEXT NOT NULL UNIQUE);
CREATE TABLE dim_source_system (source_system_key INTEGER PRIMARY KEY, source_system TEXT NOT NULL UNIQUE);
CREATE TABLE dim_date (date_key INTEGER PRIMARY KEY, calendar_date TEXT NOT NULL UNIQUE, year INTEGER NOT NULL, month INTEGER NOT NULL, day INTEGER NOT NULL);
CREATE TABLE fact_process_event (
  event_key INTEGER PRIMARY KEY, event_id TEXT NOT NULL UNIQUE, case_key INTEGER NOT NULL,
  activity_key INTEGER NOT NULL, source_system_key INTEGER NOT NULL, event_date_key INTEGER NOT NULL,
  event_timestamp TEXT NOT NULL, lifecycle TEXT, queue_or_team TEXT, amount REAL, currency TEXT, sla_due_timestamp TEXT,
  FOREIGN KEY(case_key) REFERENCES dim_case(case_key), FOREIGN KEY(activity_key) REFERENCES dim_activity(activity_key),
  FOREIGN KEY(source_system_key) REFERENCES dim_source_system(source_system_key), FOREIGN KEY(event_date_key) REFERENCES dim_date(date_key)
);
