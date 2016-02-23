## Introduction

This module is used to rank the list of at-risk properties according to some targeting priority.

With this targeting priority we want to ensure that the city focuses on commercial entities and landlords with
several properties instead of individual owners (that might not have the means to upkeep their properties).

## Usage

1. To create a database table that counts how many properties each property owner in the city owns (for
the year 2015). Create this table by executing the SQL commands in `num_properties_owned.sql`

2. After having run `blight_risk_prediction/model` locate the output csv file (should be in folder `predictions`). 

3. Set this filename in priotize.py and run


    python -m targeting_priority/prioritize
    
The ranked list of properties is written to the same location as the original csv file (but with ending `_ranked.csv`)

## How is the targeting done?

### Calculate probability rank

Properties are ranked according to their predicted probability. This ranking is done based on which quantile the 
probability falls into. The higher the probability, the higher the rank. The quantiles to be used for calculating the 
ranks is defined at the top of `priorize.py`

### Calculate targeting rank

Properties are ranked according to how many properties are owned by the owner of the properties. The higher the number
of properties owned, the higher the rank. The script uses bins to group the "number of properties owned", these bins are
defined at the top of `priorize.py`.

### Calculate combined probability

The combined probability of a property is

    probability_rank * num_targeting_bins + targeting_rank
    
This means that if _property_a_ is in a higher probability quantile than some _property_b_, _property_a_ will always be 
ranked higher than _property_b_. If _property_a and _property_b_ are in the same probability quantile, then they will
be ranked according to their targeting rank.