"""
Make a huge csv with a bunch of information about every property
"""

import sys
from sqlalchemy import create_engine
from lib_cinci.db import uri
import pandas as pd
import dbconfig

engine = create_engine(uri)


def get_neighbourhood():
    def make_address(row):
        if row["addrst"]:
            street = " ".join([a.capitalize() for a in row["addrst"].split()])
        else:
            street = " "
        if row["addrno"]:
            no = row["addrno"]
        else:
            no = " "
        if row["addrsf"]:
            typ = " ".join([a.capitalize() for a in row["addrsf"].split()])
        else:
            typ = " "
        return no + " " + street + " " +  typ

    hoods = "SELECT * FROM shape_files.parcelid_blocks_grp_tracts_nhoods"
    hoods = pd.read_sql(hoods, con=engine)
    hoods = hoods.rename(columns={"parcelid": "parcel_id"})
    hoods = hoods.set_index("parcel_id")
    hoods["address"] = hoods.apply(make_address, axis=1)
    hoods = hoods.drop(["addrno", "addrst", "addrsf"], axis=1)
    hoods.to_csv("postprocess/hoods.csv")
    return hoods


def get_last_inspection():
    inspections = ("SELECT DISTINCT ON (parcel_no) "
                   "       parcel_no AS parcel_id, "
                   "       date AS last_interaction, "
                   "       comp_type AS last_interaction_type, "
                   "       event AS last_interaction_event  "
                   "FROM  inspections_views.events_parcel_id "
                   "ORDER BY parcel_no, date DESC; ")
    inspections = pd.read_sql(inspections, con=engine)
    inspections = inspections.set_index("parcel_id")
    inspections.to_csv("postprocess/inspections.csv")
    return inspections


def get_any_interaction():
    inspections_cases = "SELECT DISTINCT(parcel_no) AS parcel_id FROM inspections_raw.t_dssg_apd_par"
    inspections_cases = pd.read_sql(inspections_cases, con=engine)
    inspections_cases = inspections_cases.set_index("parcel_id")
    inspections_cases["any_interaction"] = pd.Series(True, index=inspections_cases.index)
    return inspections_cases


def get_type():
    def is_residential(property_class):
        if int(property_class) == 423 or 500 <= int(property_class) <= 599:
            return True
        return False

    use_type = ("SELECT parcels.parcelid AS parcel_id, parcels.class "
                "FROM shape_files.parcels_cincy AS parcels")

    use_type = pd.read_sql(use_type, con=engine)
    use_type["residential"] = use_type["class"].apply(is_residential)
    use_type = use_type.set_index("parcel_id")
    use_type.to_csv("postprocess/type.csv")
    return use_type["residential"]


dataset = get_type()
dataset = pd.merge(dataset, get_neighbourhood(), how='left', left_index=True, right_index=True)
dataset = pd.merge(dataset, get_last_inspection(), how='left', left_index=True, right_index=True)
dataset.to_csv("parcel_info.csv")
