import requests
import json
import pandas as pd
from app_utils import *
import streamlit as st
import numpy as np
import datetime
from streamlit_javascript import st_javascript

st.title('Calendar C-F-R')
dates = st.date_input(label = 'Date Range', value = [datetime.date.today(), datetime.date.today()+datetime.timedelta(days = 7)],
min_value=datetime.date.today(), max_value = datetime.date.today()+datetime.timedelta(days = 13))
timezone = st_javascript("""await (async () => {
            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            console.log(userTimezone)
            return userTimezone
})().then(returnValue => returnValue)""")

df = get_all_calendars(dates[0], dates[1], timezone).copy(deep = True)
pdf = get_styled_pivot_calendar(df)

st.text("Showing for timezone: "+timezone)
st.table(pdf)