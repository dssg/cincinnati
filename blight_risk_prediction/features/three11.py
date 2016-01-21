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

def create_three11_1_month_table(con):
    #Load template with SQL statement
    with open('three11_for_inspections_x_month.sql', 'r') as f:
        sql_script = f.read()
    #Run the code using the connection
    #this is going to take a while
    con.cursor().execute(sql_script)


def make_three11_features(con):
    """
    Make 311 calls features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    #parcels_three11_view contains data
    #to match each parcel with their corresponding 311
    #calls within 3 kilometers. Use that view to now
    #match each inspection with calls that happened
    #X months before the inspection

    #Use the recently created table to compute features.
    #Group rows by parcel_id and inspection_date
    #For now, just perform counts on the categorical variables
    #More complex features could combine the distance value
    #as well as interacting features