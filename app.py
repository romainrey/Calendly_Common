import requests
import json
import pandas as pd
from app_utils import *
import streamlit as st
import numpy as np
import datetime

st.title('Calendar C-F-R')
dates = st.date_input(label = 'Date Range', value = [datetime.date.today(), datetime.date.today()+datetime.timedelta(days = 7)])
# length_slot = st.number_input(label = 'Duration (mn)', min_value = 30, max_value = 120, step = 30, value = 60)

df = get_all_calendars(dates[0], dates[1]).copy(deep = True)
# n_slots = length_slot//30
# df = find_continuous_set(df, n_slots)

df['HourF'] = df['Hour']+0.5*(df['Minute'] == 30)

def greend1s(val):
    return 'background-color: green' if val==1 else 'background-color: white'

hours = np.arange(df.HourF.min(), df.HourF.max(), 0.5)
days = df.Day.drop_duplicates()
all_dates = pd.concat([pd.DataFrame({'Day':i, 'HourF':hours}) for i in days])
df['Free'] = 1
df2 = pd.merge(all_dates, df, on = ['Day', 'HourF'], how = 'left')
df2.Free.fillna(0, inplace=True)
df2.Free = df2.Free.astype('int')
df2.HourF = df2.HourF.apply(lambda x: str(int(x)).zfill(2)+'h'+str(int(3/5 * 100*(x-int(x)))).zfill(2))
pdf = pd.pivot_table(df2, index = 'HourF', columns = 'Day', values = 'Free')

st.table(pdf.style.applymap(greend1s))