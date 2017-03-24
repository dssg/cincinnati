import pandas as pd 
import sqlalchemy

# make feature crosstabs                                                                                                                                                    
query = '''                                                                                                                                                                 
        SELECT DISTINCT (table_name)                                                                                                                                        
        FROM information_schema.tables                                                                                                                                      
        WHERE table_schema = 'features_31aug2016';                                                                                                                          
        '''                                                                                                                                                                 
all_tables = pd.read_sql(query, engine)                                                                                                                                     

all_features = {}                                                                                                                                                           

#Todo: drop all "insp2..." features
for t in list(all_tables.table_name):                                                                                                                                       
    query = 'SELECT * FROM features_31aug2016.{table};'.format(table=t)                                                                                                     
    features = pd.read_sql(query, engine, index_col = 'parcel_id')                                                                                                          
    features.columns = [t + '.' + str(col) for col in features.columns]                                                                                                     
    all_features[t] = features                                                                                                                                              

# combine all features                                                                                                                                                     
all_features = pd.concat(all_features.values())                                                                                                                             

# get mean over all parcels                                                                                                                                                 
all_features_mean = all_features.mean(axis=0)                                                                                                                               

# add a column for model group (all parcels doesn't have one)                                                                                                          
all_features_mean = all_features_mean.append(pd.Series([1.0], index=['model_group'])    
all_features_mean_df = all_features_mean.to_frame().T                                                                                                                     
feature_averages = {}                                                                                                                                                       

for m in model_groups:                                                                                                                                                      
    list_name = str(m)                                                                                                                                                      
    model_features = all_features[all_features.index.isin(top_k[list_name].index)].mean(axis=0)                                                                             
    model_features = model_features.to_frame().T                                                                                                                            
                                                                                                                                                                           
    feature_averages[list_name + ' Top 5'] = model_features                                                                                                                 
    feature_averages[list_name + ' Top 5']['model_group'] = model_num                                                                                                       
    feature_averages[list_name + ' Top 5']['subset'] = 'Top 5 Average'                                                                                                      
    feature_averages[list_name + ' Top 5']['list'] = 'All Parcels'                                                                                                          

    feature_averages[list_name + ' Ratio'] = model_features.divide(all_features_mean_df, axis=1)                                                                            
    feature_averages[list_name + ' Ratio']['model_group'] = model_num                                                                                                       
    feature_averages[list_name + ' Ratio']['subset'] = 'Ratio'                                                                                                              
    feature_averages[list_name + ' Ratio']['list'] = 'All Parcels'                                                                                                          

crosstabs = pd.concat(feature_averages.values())                                                                                                                            
crosstabs = crosstabs.append(all_features_mean_df)                                                                                                                          
crosstabs.set_index(['model_group','list','subset'], inplace=True)                                                                                                          
crosstabs.reset_index(inplace=True)                                                                                                                                        
crosstabs['new_index'] = crosstabs['model_group'].map(int).map(str) + ' ' + crosstabs['list'] + ' ' + crosstabs['subset']                                                   
crosstabs.set_index('new_index', inplace=True)                                                                                                                             
crosstabs.T.to_csv('feature_crosstabs.csv')                                                                                                                                 

