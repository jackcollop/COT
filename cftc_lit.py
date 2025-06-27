import numpy as np
import pandas as pd
import streamlit as st
#%%
import requests

fut = requests.get(r'https://publicreporting.cftc.gov/resource/72hh-3qpy.json?commodity_name=COTTON', cert=False).text


fut = pd.read_json(fut)
fut['Date'] = pd.to_datetime(fut.report_date_as_yyyy_mm_dd)
fut.sort_values(by=['Date'], inplace=True)
fut.set_index('Date', inplace=True)

fut['merc_net'] = fut['prod_merc_positions_long'] - fut['prod_merc_positions_short']
fut['swap_net'] = fut['swap_positions_long_all'] - fut['swap__positions_short_all']
fut['other_net'] = fut['other_rept_positions_long'] - fut['other_rept_positions_short']
fut['money_net'] = fut['m_money_positions_long_all'] - fut['m_money_positions_short_all']
fut['non_net'] = fut['nonrept_positions_long_all'] - fut['nonrept_positions_short_all']

fut['money_net_old'] = fut['m_money_positions_long_old'] - fut['m_money_positions_short_old']
fut['money_net_new'] = fut['m_money_positions_long_other'] - fut['m_money_positions_short_other']

index = requests.get(r'https://publicreporting.cftc.gov/resource/4zgm-a668.json?commodity_name=COTTON&$limit=1500', cert=False).text

index = pd.read_json(index)
index['Date'] = pd.to_datetime(index.report_date_as_yyyy_mm_dd)
index.sort_values(by=['Date'], inplace=True)
index.set_index('Date', inplace=True)

index['cit_net'] = index.cit_positions_long_all - index.cit_positions_short_all

st.dataframe(fut[['merc_net','swap_net','other_net','money_net','non_net']].join(index[['cit_net','open_interest_all']]).diff().sort_index(ascending=False), column_config={'Date':st.column_config.DateColumn('Date')})


st.line_chart(fut[['money_net_old']].tail(52))
st.line_chart(fut[['money_net_new']].tail(52))



st.line_chart(fut[['money_net','open_interest_all']].join(index['cit_net']))
