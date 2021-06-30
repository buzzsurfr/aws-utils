-- Name: DF Billing/Proj (All)
-- Description: Provides summary of all device time, separated by project.
SELECT project.name AS project,
        SUM(deviceminutes.metered) AS metered,
        SUM(deviceminutes.unmetered) AS unmetered
FROM runs
GROUP BY  project.name;

-- Name: DF Billing/Run (All)
-- Description: Provides summary of all device time, separated by run.
SELECT project.name AS project,
        name AS run,
        SUM(deviceminutes.metered) AS metered,
        SUM(deviceminutes.unmetered) AS unmetered
FROM runs
GROUP BY  project.name,name;

-- Name: DF Billing/Proj (Last Month)
-- Description: Provides summary of last month's device time, separated by project.
SELECT project.name AS project,
        SUM(deviceminutes.metered) AS metered,
        SUM(deviceminutes.unmetered) AS unmetered
FROM runs
WHERE year = year(current_date - interval '1' month)
AND month = month(current_date - interval '1' month)
GROUP BY  project.name;

-- Name: DF Billing/Run (Last Month)
-- Description: Provides summary of last month's device time, separated by run.
SELECT project.name AS project,
        name AS run,
        SUM(deviceminutes.metered) AS metered,
        SUM(deviceminutes.unmetered) AS unmetered
FROM runs
WHERE year = year(current_date - interval '1' month)
AND month = month(current_date - interval '1' month)
GROUP BY  project.name,name;


-- Name: DF Billing/Proj (This Month)
-- Description: Provides summary of this month's device time, separated by project.
SELECT project.name AS project,
        SUM(deviceminutes.metered) AS metered,
        SUM(deviceminutes.unmetered) AS unmetered
FROM runs
WHERE year = year(current_date)
AND month = month(current_date)
GROUP BY  project.name;

-- Name: DF Billing/Run (This Month)
-- Description: Provides summary of this month's device time, separated by run.
SELECT project.name AS project,
        name AS run,
        SUM(deviceminutes.metered) AS metered,
        SUM(deviceminutes.unmetered) AS unmetered
FROM runs
WHERE year = year(current_date)
AND month = month(current_date)
GROUP BY  project.name,name;
