import requests
import json
import pandas as pd
import streamlit as st
import numpy as np

"""
Pull data of availability between date1 and date2 for one calendly
The link of the request needs to be found in the request the browser makes to the calendly
"""
def get_request(link, date1, date2, timezone):
    headers = {
        'authority': 'calendly.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://calendly.com/romain_rey/30mn?month=2022-12',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'timezone': timezone,
        'diagnostics': 'false',
        'range_start': date1,
        'range_end': date2,
    }

    response = requests.get(
        link,
        params=params,
        headers=headers,
    )
    return(response)

"""
Cast the data into a dataframe
"""
def get_spots(response, name):
    days = json.loads(response.text)['days']
    dfs = []

    for d in days:
        if d['status']=='unavailable':
            continue
        else:
            spots = []      
            for s in d['spots']:
                if s['status'] == 'available':
                    spots.append(s['start_time'])
        dfs.append(pd.DataFrame({name:spots}))

    df = pd.concat(dfs).reset_index().drop('index', axis = 1)
    df[name] = pd.to_datetime(df[name])
    return(df)

"""
Return calendar data into dataframe
"""
def get_calendar(link, name, date1, date2, timezone):
    response = get_request(link, date1, date2, timezone)
    df = get_spots(response, name)
    return(df)

"""
Pulls our 3 calendars and give a dataframe of the common times
"""
def get_all_calendars(date1, date2, timezone):
    link_romain = 'https://calendly.com/api/booking/event_types/CGC3VNJAQJDMOMAA/calendar/range'
    link_clovis = 'https://calendly.com/api/booking/event_types/203ad347-f3e7-456e-9e43-95bad33d1eba/calendar/range'
    link_fernando = 'https://calendly.com/api/booking/event_types/64be395f-d4d3-4d05-8b93-770e307e9c3d/calendar/range'

    rom = get_calendar(link_romain, 'Romain', date1, date2, timezone)
    clo = get_calendar(link_clovis, 'Clovis', date1, date2, timezone)
    fer = get_calendar(link_fernando, 'Fernando', date1, date2, timezone)

    commonTimes = set(rom['Romain']) & set(clo['Clovis']) & set(fer['Fernando'])
    df = pd.DataFrame(commonTimes).rename({0:'Times'}, axis = 1)
    df['Day'] = df.Times.dt.date
    df['Hour'] = df.Times.dt.hour
    df['Minute'] = df.Times.dt.minute
    df = df.sort_values('Times')
    return(df)

"""
Find times where continuous period of common time is available
"""
def find_continuous_set(df, n_continuous_30mn_slots):
    n_continuous_30mn_slots = 2
    sets = set()
    serie = 1
    past = pd.to_datetime('2022-10-01 11:30:00-05:00')
    beg_series = past
    for i in range(df.shape[0]):
        this = df.Times.iloc[i]
        is_next_half_hour = (this-past).total_seconds() == 30*60
        if is_next_half_hour:
            serie +=1
        else:
            serie = 1
        if serie>=n_continuous_30mn_slots:
            sets.add(df.Times.iloc[i-n_continuous_30mn_slots+1]) 
        past = this

    df = pd.DataFrame(sets).rename({0:'Times'}, axis = 1)
    df['Day'] = df.Times.dt.date
    df['Hour'] = df.Times.dt.hour
    df['Minute'] = df.Times.dt.minute
    df = df.sort_values('Times')
    return(df)

"""
Return the calendar in a pivot form with days as columns and times as rows
"""
def get_styled_pivot_calendar(df):
    # Putting time into float
    df['HourF'] = df['Hour']+0.5*(df['Minute'] == 30)
    def greend1s(val):
        return 'background-color: green' if val==1 else 'background-color: white'
    # Adding all the missing rows to the df so the pivot is complete
    hours = np.arange(df.HourF.min(), df.HourF.max(), 0.5)
    days = df.Day.drop_duplicates()
    all_dates = pd.concat([pd.DataFrame({'Day':i, 'HourF':hours}) for i in days])
    df['Free'] = 1
    df2 = pd.merge(all_dates, df, on = ['Day', 'HourF'], how = 'left')
    df2.Free.fillna(0, inplace=True)
    df2.Free = df2.Free.astype('int')
    # Recasting time into readable format 00h00
    df2.HourF = df2.HourF.apply(lambda x: str(int(x)).zfill(2)+'h'+str(int(3/5 * 100*(x-int(x)))).zfill(2))
    pdf = pd.pivot_table(df2, index = 'HourF', columns = 'Day', values = 'Free').style.applymap(greend1s)
    return(pdf)