import pandas as pd
from dstools.db import uri
from sqlalchemy import create_engine

engine = create_engine(uri)

#Remove hardcoded schema
df = pd.read_sql('SELECT * FROM features.three11_for_inspections_1_month', engine)

#Group by parcel_id and inspection_date. Make columns with counts for service_code
#and agency_responsible
cross = pd.crosstab([df.parcel_id, df.inspection_date],
                    [df.service_code, df.agency_responsible],
                   margins=True)
