import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import requests

st.set_page_config(layout='wide')

fut = requests.get(r'https://publicreporting.cftc.gov/resource/72hh-3qpy.json?commodity_name=COTTON', cert=False).text


fut = pd.read_json(fut)
fut['Date'] = pd.to_datetime(fut.report_date_as_yyyy_mm_dd)
fut.sort_values(by=['Date'], inplace=True)
fut.set_index('Date', inplace=True)

fut['merchant'] = fut['prod_merc_positions_long'] - fut['prod_merc_positions_short']
fut['swap_dealer'] = fut['swap_positions_long_all'] - fut['swap__positions_short_all']
fut['other_reportable'] = fut['other_rept_positions_long'] - fut['other_rept_positions_short']
fut['money'] = fut['m_money_positions_long_all'] - fut['m_money_positions_short_all']
fut['non_reportable'] = fut['nonrept_positions_long_all'] - fut['nonrept_positions_short_all']

fut['money_net_old'] = fut['m_money_positions_long_old'] - fut['m_money_positions_short_old']
fut['money_net_new'] = fut['m_money_positions_long_other'] - fut['m_money_positions_short_other']

date = fut.report_date_as_yyyy_mm_dd.iloc[-1]

date = str(date)

r1 = pd.read_json(r'https://publicreporting.cftc.gov/resource/kh3c-gbw2.json?report_date_as_yyyy_mm_dd='+date)
#%%
r1['m_net'] = r1['change_in_m_money_long_all'] - r1['change_in_m_money_short_all']

r1['m_net_pct_oi'] = r1['m_net'] / r1['open_interest_all']
#%%
fig1 = px.bar(r1[r1.commodity_group_name == 'AGRICULTURE'].set_index('commodity_name').m_net)
#%%
fig2 = px.bar(r1[r1.commodity_group_name == 'AGRICULTURE'].set_index('contract_market_name')[['m_net','m_net_pct_oi']].drop(['BUTTER (CASH SETTLED)','NON FAT DRY MILK', 'CME MILK IV']), hover_data='m_net')
st.dataframe(r1[r1.commodity_group_name != 'AGRICULTURE'].set_index('contract_market_name')[['m_net','m_net_pct_oi']])

#%%

i1 = pd.read_json('https://publicreporting.cftc.gov/resource/4zgm-a668.json?report_date_as_yyyy_mm_dd='+date)
#%%
i1['index_net'] = i1['change_cit_long_all'] - i1['change_cit_short_all']

i1['index_net_pct_oi'] = i1['index_net'] / i1['open_interest_all']
#%%
fig3 = px.bar(i1[i1.commodity_group_name == 'AGRICULTURE'].set_index('contract_market_name')[['index_net_pct_oi','index_net']], hover_data='index_net')

index = requests.get(r'https://publicreporting.cftc.gov/resource/4zgm-a668.json?commodity_name=COTTON&$limit=1500', cert=False).text

index = pd.read_json(index)
index['Date'] = pd.to_datetime(index.report_date_as_yyyy_mm_dd)
index.sort_values(by=['Date'], inplace=True)
index.set_index('Date', inplace=True)

index['index'] = index.cit_positions_long_all - index.cit_positions_short_all

st.caption("Net weekly flow by type")
st.dataframe(fut[['money','merchant','swap_dealer','other_reportable','non_reportable']].join(index[['index','open_interest_all']]).diff().sort_index(ascending=False), column_config={'Date':st.column_config.DateColumn('Date')})

fut['week'] = fut['yyyy_report_week_ww'].str.split(' ', expand=True)[3]
fut['year'] = fut.index.year

fut['money'] = fut['m_money_positions_long_all'] - fut['m_money_positions_short_all']
fig = px.line(fut.reset_index()[['week','year','money']].pivot(index='week', columns='year', values='money'))

fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = np.arange(1, 53, 4.4167),
        ticktext = ['Jan','Feb','Mar','Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov','Dec'],
    )
)

fig['data'][-1]['line']['width']=5

st.caption("Cotton managed money net position")
st.plotly_chart(fig)

st.caption("Managed money weekly futures flow by commodity (normalized as % total open interest)")
st.plotly_chart(fig2)

st.caption("Index weekly net futures flow by commodity (normalized as % total open interest)")
st.plotly_chart(fig3)
