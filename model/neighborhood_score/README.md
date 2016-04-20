#Neighborhood scoring

Using `neighborhood_score.py`, a table will be created to score the 'neighborhood' of each inspection. The objective of this is to provide a metric of how blighted is the area nearby certain parcel within X months of inspection date and Y meters.

This score will later be used to weight predictions from models. This is **not** intended to be used as a feature.

Run:
```bash
./neighborhood_score.py --help
```

For details on how to use this script.