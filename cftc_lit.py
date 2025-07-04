import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import requests

fut = requests.get(r'https://publicreporting.cftc.gov/resource/72hh-3qpy.json?commodity_name=COTTON', cert=False).text


fut = pd.read_json(fut)
fut['Date'] = pd.to_datetime(fut.report_date_as_yyyy_mm_dd)
fut.sort_values(by=['Date'], inplace=True)
fut.set_index('Date', inplace=True)

fut['merchant'] = fut['prod_merc_positions_long'] - fut['prod_merc_positions_short']
fut['swap_dealer'] = fut['swap_positions_long_all'] - fut['swap__positions_short_all']
fut['other_rept'] = fut['other_rept_positions_long'] - fut['other_rept_positions_short']
fut['money'] = fut['m_money_positions_long_all'] - fut['m_money_positions_short_all']
fut['non_rept'] = fut['nonrept_positions_long_all'] - fut['nonrept_positions_short_all']

fut['money_net_old'] = fut['m_money_positions_long_old'] - fut['m_money_positions_short_old']
fut['money_net_new'] = fut['m_money_positions_long_other'] - fut['m_money_positions_short_other']

index = requests.get(r'https://publicreporting.cftc.gov/resource/4zgm-a668.json?commodity_name=COTTON&$limit=1500', cert=False).text

index = pd.read_json(index)
index['Date'] = pd.to_datetime(index.report_date_as_yyyy_mm_dd)
index.sort_values(by=['Date'], inplace=True)
index.set_index('Date', inplace=True)

index['index'] = index.cit_positions_long_all - index.cit_positions_short_all

st.dataframe(fut[['money','merchant','swap_dealer','other_rept','non_rept']].join(index[['index','open_interest_all']]).diff().sort_index(ascending=False), column_config={'Date':st.column_config.DateColumn('Date')})

fut['week'] = fut['yyyy_report_week_ww'].str.split(' ', expand=True)[3]
fut['year'] = fut.index.year

fut['money'] = fut['m_money_positions_long_all'] - fut['m_money_positions_short_all']
fig = px.line(fut.reset_index()[['week','year','money']].pivot(index='week', columns='year', values='money'))

fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = np.arange(1, 53, 4.34524),
        ticktext = ['Jan','Feb','Mar','Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov','Dec'],
    )
)

fig['data'][-1]['line']['width']=5
st.plotly_chart(fig)
