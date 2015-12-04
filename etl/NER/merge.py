import pandas as pd


def read_for_year(year):
    df = pd.read_csv("owners_{}_resolved.csv".format(year))
    df["parcel_id"] = df["parcel_id"].astype(str)

    #dupes = df.groupby(level=0).filter(lambda x: len(x) > 1)
    df = df.drop_duplicates(subset='parcel_id')

    df = df.set_index("parcel_id")
    entities = df["entity"]
    entities.name = "owner_"+str(year)
    
    return entities


owners = [read_for_year(y) for y in range(2007, 2016)]
merged = pd.concat(owners, axis=1)
merged = merged.reset_index()
merged = merged.rename(columns={"index": "parcel_id"})
merged.to_csv("owners_2007-2015.csv", index=False)

