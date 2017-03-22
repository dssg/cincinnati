DROP TABLE IF EXISTS tax_foreclosure;

--Create tax_foreclosure table
CREATE TABLE tax_foreclosure AS(
    SELECT parcel_id, forcl_flag, year FROM tax_combined
)
