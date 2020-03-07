'''
Memo: List of exchanges included in original full file:
['ADX', 'AIM', 'AMEX', 'ASE', 'ASX', 'ATSE', 'BASE', 'BATS', 'BAX',
'BDB', 'BDL', 'BDM', 'BELEX', 'BER', 'BIT', 'BME', 'BMV',
'BOVESPA', 'BRSE', 'BRVM', 'BSE', 'BSM', 'BSSE', 'BST', 'BUL',
'BUSE', 'BVB', 'BVC', 'BVL', 'BVMT', 'CASE', 'CBSE', 'CCSE',
'CISX', 'CNSX', 'COSE', 'CPSE', 'CSE', 'Catalist', 'DAR', 'DB',
'DFM', 'DIFX', 'DSE', 'DSM', 'DUSE', 'ENXTAM', 'ENXTBR', 'ENXTLS',
'ENXTPA', 'FKSE', 'GHSE', 'GTSM', 'GYSE', 'HLSE', 'HMSE', 'HNX',
'HOSE', 'IBSE', 'ICSE', 'IDX', 'ISE', 'JASDAQ', 'JMSE', 'JSE',
'KAS', 'KASE', 'KLSE', 'KOSDAQ', 'KOSE', 'KWSE', 'LJSE', 'LSE',
'LUSE', 'MAL', 'MISX', 'MSM', 'MTSE', 'MUN', 'MUSE', 'NASE', 'NGM',
'NGSE', 'NMSE', 'NSE', 'NSEI', 'NSEL', 'NSX', 'NYSE', 'NZSE',
'NasdaqCM', 'NasdaqGM', 'NasdaqGS', 'OB', 'OM', 'OTCNO', 'OTCPK',
'PLSE', 'PSE', 'RISE', 'SASE', 'SEHK', 'SEP', 'SET', 'SGX', 'SHSE',
'SNSE', 'SPSE', 'SWX', 'SZSE', 'TASE', 'TLSE', 'TSE', 'TSEC',
'TSX', 'TSXV', 'TTSE', 'UGSE', 'UKR', 'WBAG', 'WSE', 'XKON',
'XTRA', 'ZGSE', 'ZMSE', nan]
'''


import pandas as pd

industries = pd.read_excel('data/indname.xls', \
                                        sheet_name='Industry sorted (Global)')
industries.rename(columns={'Industry Group': 'industry', \
                           'Company Name': 'company', \
                           'Exchange:Ticker': 'ticker'}, inplace=True)
industries = industries[['industry', 'company', 'ticker']]
industries.dropna(subset=['ticker'], inplace=True)
target_string = r'ISE|NYSE|NasdaqCM|NasdaqGM|NasdaqGS'
industries = industries[industries['ticker'].str.contains(target_string)]
industries['ticker'] = industries['ticker'].str.extract(r':(.*)', expand=False)

industries.to_csv('data/Industries.csv', index=False)