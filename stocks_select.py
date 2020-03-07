'''
Leveraging the power of pandas and numpy, clean the two csvs: ESG_Stocks.csv
and Full_Stocks.csv. Record the output in NonUS_ESG_Firms.csv
'''

import pandas as pd
import numpy as np

esg_df = pd.read_csv('data/ESG_Stocks.csv')
full_df = pd.read_csv('data/Full_Stocks.csv')

# esg_df
# rename columns
rename_dict = {'Unnamed: 1': 'SEDOL', 'Unnamed: 2': 'ticker', 
'Unnamed: 3': 'name', 'Unnamed: 4': 'shares', 
'Unnamed: 5': 'market_value', 'Unnamed: 6': 'percent_funds',
'Unnamed: 7': 'sector', 'Unnamed: 8': 'market', 
'Unnamed: 9': 'receipt_type'}
esg_df.rename(columns=rename_dict, inplace=True)
esg_df['ESG'] = 'Y'
# drop bonds, currencies, commodities, short-term reserves
esg_df.drop(list(range(3861, 3874)), inplace=True)
# drop redundant first column
esg_df.drop(columns=['Stocks holdings '], inplace=True)
# reset index
esg_df.reset_index(drop=True, inplace=True)

# non_esg_df
# rename columns
full_df.rename(columns=rename_dict, inplace=True)
full_df['ESG'] = 'N'
full_df.drop(list(range(7402, 7417)), inplace=True)
full_df.drop(columns=['Stocks holdings '], inplace=True)
full_df.reset_index(drop=True, inplace=True)

# only keep relevant information for this project
drop_cols = ['shares', 'market_value', 'percent_funds', 'sector', 'market', \
    'receipt_type']
esg_df.drop(columns=drop_cols, inplace=True)
full_df.drop(columns=drop_cols, inplace=True)

# change the ESG attribute to Y for some stocks in full df
# full_df[full_df['SEDOL'].isin(esg_df['SEDOL'])], this only selects
# can't set values, so you have to use the one below
full_df.loc[full_df['SEDOL'].isin(esg_df['SEDOL']), 'ESG'] = 'Y'
# forgot to drop the description row, which is redundant at this point
full_df.drop([0], inplace=True)

full_df.to_csv('data/NonUS_ESG_Firms.csv')