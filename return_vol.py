'''
Return and volatility graph, using 50% cutoff and total score.
'''


import pandas as pd
import numpy as np
from decimal import Decimal


out = pd.read_csv('data/SP500_ESG.csv')
out.dropna(inplace=True)
ret = pd.read_csv('data/returns.csv')
ret['RET'].replace({'C': 0, 'B' : 0}, inplace=True)
ret.dropna(subset=['TICKER'], inplace=True)

esg_cutoff = out['total_score'].quantile(0.5)
esg_df = out[out['total_score']> esg_cutoff]
non_esg_df = out[out['total_score'] <= esg_cutoff]

ret_2018 = ret[(ret['date'] > 20130101) & (ret['date'] < 20181231)]
num_trading_days = ret_2018['date'].unique().shape[0]
ret_2018 = ret_2018[['date', 'TICKER', 'RET']]
ret_2018['RET'] = ret_2018['RET'].astype('float64', copy=True)

esg_df = esg_df.merge(ret_2018, left_on='ticker', right_on='TICKER', \
                                                                how='right')
esg_df = esg_df[['date', 'TICKER', 'weight', 'RET']]
esg_df.dropna(inplace=True)

non_esg_df = non_esg_df.merge(ret_2018, left_on='ticker', \
                                            right_on='TICKER', how='right')
non_esg_df = non_esg_df[['date', 'TICKER', 'weight', 'RET']]
non_esg_df.dropna(inplace=True)

return_vol = pd.DataFrame()
list_returns = []
list_vols = []
list_lambdas = []

for lambda_ in np.linspace(0, 1, 11):
    esg_df['weight_esg'] = esg_df['weight'] * lambda_
    non_esg_df['weight_esg'] = non_esg_df['weight'] * (1 - lambda_)
    full_df = esg_df.append(non_esg_df)
    full_df['weight_esg'] = full_df['weight_esg'] / full_df['weight_esg'].sum()
    full_df.set_index(pd.to_datetime(full_df['date'], \
                                                format='%Y%m%d'), inplace=True)
    full_df.drop(columns=['date'], inplace=True)
    full_df['weight_esg'] = full_df['weight_esg'] * num_trading_days
    full_df['RET_esg'] = full_df['weight_esg'] * full_df['RET']
    annual_returns = full_df.groupby(full_df.index.year)['RET_esg'].sum()
    ann_return_cooler = (1 + annual_returns).prod() ** (1/6) - 1
    daily_port_ret = full_df.groupby(full_df.index.date)['RET_esg'].sum()
    ann_vol = daily_port_ret.std() * (1 / (num_trading_days * 6)) ** (1 / 2)
    
    list_returns.append(ann_return_cooler)
    list_vols.append(ann_vol)
    list_lambdas.append(lambda_)

return_vol['lambda'] = list_lambdas
return_vol.set_index('lambda', inplace=True)
return_vol['returns'] = list_returns
return_vol['vol'] = list_vols

plt = return_vol.plot(x='vol', y='returns', style='.-')
plt.set_ylabel('Annualized Returns')
plt.set_xlabel('Volatility')

for index, row in return_vol.iterrows():
    returns = row['returns']
    vol = row['vol']
    index = round(Decimal(index), 1)
    plt.annotate('lambda = {}'.format(index), xy=(vol, returns), \
                                  xytext=(2.5,-5), textcoords='offset points') 

plt.figure.savefig(r'data/Return vs. Volatility.png')