import pandas as pd

predictions = "2015-08-25T04:15:44.220467.csv"
output = "2015-08-25T04:15:44.220467_details.csv"

to_inspect = pd.read_csv(predictions, header=None,
                         names={"parcel_id", "inspection_date", "probability"}, index_col=0)

parcel_info = pd.read_csv("postprocess/parcel_info.csv", index_col=0)
to_inspect = pd.merge(to_inspect, parcel_info, how='left', left_index=True, right_index=True)
to_inspect["last_inspection"] = pd.to_datetime(to_inspect["last_inspection"])

to_inspect.to_csv(output)
