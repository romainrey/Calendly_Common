import requests
import json
import pandas as pd
from app_utils import *
import streamlit as st
import numpy as np
import datetime

st.title('Calendar C-F-R')
dates = st.date_input(label = 'Date Range', value = [datetime.date.today(), datetime.date.today()+datetime.timedelta(days = 7)],
min_value=datetime.date.today(), max_value = datetime.date.today()+datetime.timedelta(days = 13))

df = get_all_calendars(dates[0], dates[1]).copy(deep = True)
pdf = get_styled_pivot_calendar(df)

st.table(pdf.style.applymap(greend1s))