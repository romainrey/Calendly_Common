import requests
import json
import pandas as pd
from app_utils import *
import streamlit as st
import numpy as np
import datetime
from streamlit_javascript import st_javascript

st.title('Calendar C-F-R')
min_date, max_date = datetime.date.today(), datetime.date.today()+datetime.timedelta(days = 13)
dates = st.date_input(label = 'Date Range', value = (datetime.date.today(), datetime.date.today()+datetime.timedelta(days = 7)),
min_value=min_date, max_value = max_date)

timezone = st_javascript("""await (async () => {
                const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                console.log(userTimezone)
                return userTimezone
    })().then(returnValue => returnValue)""")

if len(dates)==2:
    d0 = min(dates[0], max_date-datetime.timedelta(days = 1))
    d1 = max(dates[1], d0+datetime.timedelta(days = 1))
    dates = (d0, d1)

    # Waiting for timezone to being loaded
    if len(timezone)>2:
        df = get_all_calendars(dates[0], dates[1], timezone).copy(deep = True)
        pdf = get_styled_pivot_calendar(df)

        st.text("Showing for timezone: "+timezone)
        st.table(pdf)