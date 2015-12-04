import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from blight_risk_prediction import util

# rank 0: 1 property owned by this owner
# rank 1: >= 2 properties owned by this owner
# rank 2: >= 5 properties owned by this owner
# rank 3: >= 10 properties owned by this owner
targeting_priority_bins = [1, 2, 5, 10]
targeting_priority_default_rank = 1   # if owner unknown

# rank 0: property is in lowest x% of probabilities
# highest rank: property is in highest x% of probabilities
probability_quantiles = [0.05 * (i+1) for i in range(20)]
probability_default_rank = 10
#probability_quantiles = [0.25 * (i+1) for i in range(4)]

def load_targeting_priority():
    schema = "features_01Aug2015"
    engine = util.get_engine()
    pri = pd.read_sql_table("targeting_priority", schema=schema, con=engine)
    pri = pri.drop_duplicates(["parcel_id", "inspection_date"])  # there are 12 duplicates, don't care
    pri = pri.set_index(["parcel_id", "inspection_date"])
    pri = pri["num_properties_owned"]

    rank = np.digitize(pri, targeting_priority_bins)
    rank = pd.Series(rank, pri.index)
    rank.name = "targeting_rank"

    return rank


def load_predictions(predictions_csv):
    preds = pd.read_csv(predictions_csv, header=None,
                        names=["parcel_id", "inspection_date", "probability"],
                        parse_dates=["inspection_date"])
    preds = preds.set_index(["parcel_id", "inspection_date"])
    preds = preds["probability"]

    bins = preds.quantile(probability_quantiles).values
    rank = np.digitize(preds, bins)
    rank = pd.Series(rank, index=preds.index)
    rank.name = "probability_rank"
    return rank


def combined_rank(row):
    return row["probability_rank"] * len(targeting_priority_bins) + row["targeting_rank"]


def prioritize(predictions):
    predictions = load_predictions(predictions)
    targeting = load_targeting_priority()  # includes also parcels for which no probabilities predicted, e.g. streets

    combined = pd.concat([predictions, targeting], axis=1)
    combined = combined.dropna(subset=["probability_rank"])  # drop those without predicted probabilities

    combined["targeting_rank"] = combined["targeting_rank"].fillna(targeting_priority_default_rank)

    combined["rank"] = combined.apply(combined_rank, axis=1) -1
    #v = combined["rank"].value_counts()
    #v = v.sort_index()
    #print (v[30:50])

    plot_histograms(combined)
    return combined["rank"]


def plot_histograms(ranks):
    ranks["targeting_rank"].hist()
    plt.savefig("targeting_rank.png")
    plt.close()
    ranks["probability_rank"].hist()
    plt.savefig("probability_rank.png")
    plt.close()
    ranks["rank"].hist()
    plt.savefig("rank.png")
    plt.close()

predictions_csv = "predictions/2015-08-25T04:15:44.220467.csv"
final_rank = prioritize(predictions_csv)
final_rank.to_csv(predictions_csv.replace(".csv", "_ranked.csv"))
