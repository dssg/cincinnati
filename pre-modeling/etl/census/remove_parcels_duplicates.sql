DELETE FROM shape_files.parcels_cincy
    WHERE gid IN (
        SELECT MIN(gid) AS gid
        FROM shape_files.parcels_cincy
        GROUP BY parcelid
        HAVING COUNT(*)>1
    );
