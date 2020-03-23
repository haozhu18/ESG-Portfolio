'''
Lambda and sharpe ratio graph, using 50% cutoff and total score.
'''


import pandas as pd
import numpy as np
from decimal import Decimal


def prepare(RF=0):
    '''
    Return a dataframe that we will later use for the graph.
    '''

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

    lamb_sharpe = pd.DataFrame()
    list_sharpe = []
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
        daily_port_ret = full_df.groupby(full_df.index.date)['RET_esg'].sum()
        mean_daily_ret = daily_port_ret.mean()
        sd_daily_ret = daily_port_ret.std()
        sharpe = (mean_daily_ret - RF) / sd_daily_ret * (num_trading_days ** 0.5)
        
        list_sharpe.append(sharpe)
        list_lambdas.append(lambda_)

    lamb_sharpe['lambda'] = list_lambdas
    lamb_sharpe['sharpe'] = list_sharpe

    return lamb_sharpe

lamb_sharpe = prepare()
plt = lamb_sharpe.plot(x='lambda', y='sharpe', style='.-')
plt.set_ylabel('Sharpe Ratios')
plt.set_xlabel('Lambdas')

plt.figure.savefig(r'data/Lambda vs. Sharpe Ratio.png')