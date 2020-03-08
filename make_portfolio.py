'''
Make portfolio from SP500 based on ESG scores
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


CAT_CORR = {0: '(by total score)', 1: '(by environ score)', \
            2: '(by social score)', 3: '(by govern score)'}


def clean(sp='SP500', scores='ESG Scores', ind='Industries'):
    '''
    Inputs:
        sp: SP500 dataset (big)
        scores: ESG Scores on 20181001
    '''

    sp = pd.read_csv('data/{}.csv'.format(sp))
    esg = pd.read_csv('data/{}.csv'.format(scores), encoding = 'cp1252')
    esg.drop(columns=['UNIQUE_ID', 'Date', 'Company', 'CapitalIQ_ID', \
                      'Ticker'], inplace=True)
    industries = pd.read_csv('data/{}.csv'.format(ind))

    sp = sp[sp['As_Of_Date'] == 20181001]
    sp.dropna(inplace=True)
    sp.drop(columns=['As_Of_Date', 'Composite_Ticker', 'CUSIP', 'SEDOL'], \
                                                                inplace=True)

    out = pd.merge(sp, esg, on='ISIN', how='left')

    rename_dict = {'Constituent_Ticker': 'ticker', 'Weight': 'weight', \
        'Total_ESG_Score': 'total_score', 'Governance_Score': 'govern_score', \
        'Social_Score': 'social_score', 'Environment_Score': 'environ_score'}
    out.rename(columns=rename_dict, inplace=True)

    out = pd.merge(out, industries, on='ticker', how='left')
    # sorry for the hard code, but there was only one duplicate
    out.drop([112], inplace=True)

    out.to_csv('data/SP500_ESG.csv', index=False)


def build_portfolio(cutoff, category=0, returns='returns'):
    '''
    Inputs:
        cutoff: ESG cutoff in percentage
        category: 0 - do things by total score
                  1 - do things by environment score
                  2 - do things by social score
                  3 - do things by governance score
        returns: company returns data
    '''
    
    out = pd.read_csv('data/SP500_ESG.csv')
    out.dropna(inplace=True)
    out['weight'] = out['weight'] / out['weight'].sum()
    ret = pd.read_csv('data/{}.csv'.format(returns))
    ret['RET'].replace({'C': 0, 'B' : 0}, inplace=True)
    ret.dropna(subset=['TICKER'], inplace=True)
    
    if category == 1:
        esg_cutoff = out['environ_score'].quantile(cutoff)
        esg_df = out[out['environ_score']> esg_cutoff]
        non_esg_df = out[out['environ_score'] <= esg_cutoff]
    elif category == 2:
        esg_cutoff = out['social_score'].quantile(cutoff)
        esg_df = out[out['social_score']> esg_cutoff]
        non_esg_df = out[out['social_score'] <= esg_cutoff]
    elif category == 3:
        esg_cutoff = out['govern_score'].quantile(cutoff)
        esg_df = out[out['govern_score']> esg_cutoff]
        non_esg_df = out[out['govern_score'] <= esg_cutoff]
    else:
        esg_cutoff = out['total_score'].quantile(cutoff)
        esg_df = out[out['total_score']> esg_cutoff]
        non_esg_df = out[out['total_score'] <= esg_cutoff]

    ret_2018 = ret[(ret['date'] >= 20130101) & (ret['date'] <= 20181231)]
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

    # benchmark (code may not be very efficient)
    sp_df = esg_df.append(non_esg_df)
    sp_df['RET'] = sp_df['RET'] * sp_df['weight']
    full_df_ret = sp_df.groupby(['date'])['RET'].sum()
    full_df_ret = full_df_ret.to_frame(name='benchmark')
    full_df_ret['benchmark'] = full_df_ret['benchmark'].cumsum()
    full_df_ret.set_index(pd.to_datetime(full_df_ret.index, \
                                                format='%Y%m%d'), inplace=True)
    
    for lambda_ in np.linspace(0, 1, 3):
        esg_df['weight_esg'] = esg_df['weight'] * lambda_
        non_esg_df['weight_esg'] = non_esg_df['weight'] * (1 - lambda_ )
        full_df = esg_df.append(non_esg_df)
        full_df['weight_esg'] = full_df['weight_esg'] / full_df['weight_esg'].sum()
        full_df['weight_esg'] = full_df['weight_esg'] * num_trading_days
        full_df['RET_esg'] = full_df['weight_esg'] * full_df['RET']
        daily_returns = full_df.groupby(['date'])['RET_esg'].sum()
        col_name = 'lambda = {}'.format(lambda_)
        daily_returns = daily_returns.to_frame(name=col_name)
        daily_returns[col_name] = daily_returns[col_name].cumsum()
        daily_returns.set_index(pd.to_datetime(daily_returns.index, \
                                                format='%Y%m%d'), inplace=True)
        full_df_ret = full_df_ret.join(daily_returns)

    graph_title = r'Weight&Returns - {}% cutoff {}.png'.format(cutoff * 100, \
                                                          CAT_CORR[category])
    out_plt = full_df_ret.plot(title=graph_title,figsize=(6,6))
    out_plt.set_ylabel('Daily Percent Return')
    plt.savefig(r'data/' + graph_title)


for cutoff in [0.25, 0.5, 0.75]:
    for category in [0, 1, 2, 3]:
        print('Calculating with cutoff {} and category {}...'.format(cutoff, category))
        build_portfolio(cutoff, category)