import requests
import json
import pandas as pd
import streamlit as st

def get_request(link, date1, date2):
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
        'timezone': 'America/New_York',
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

def get_calendar(link, name, date1, date2):
    response = get_request(link, date1, date2)
    df = get_spots(response, name)
    return(df)

def get_all_calendars(date1, date2):
    link_romain = 'https://calendly.com/api/booking/event_types/CGC3VNJAQJDMOMAA/calendar/range'
    link_clovis = 'https://calendly.com/api/booking/event_types/203ad347-f3e7-456e-9e43-95bad33d1eba/calendar/range'
    link_fernando = 'https://calendly.com/api/booking/event_types/64be395f-d4d3-4d05-8b93-770e307e9c3d/calendar/range'

    rom = get_calendar(link_romain, 'Romain', date1, date2)
    clo = get_calendar(link_clovis, 'Clovis', date1, date2)
    fer = get_calendar(link_fernando, 'Fernando', date1, date2)

    commonTimes = set(rom['Romain']) & set(clo['Clovis']) & set(fer['Fernando'])
    df = pd.DataFrame(commonTimes).rename({0:'Times'}, axis = 1)
    df['Day'] = df.Times.dt.date
    df['Hour'] = df.Times.dt.hour
    df['Minute'] = df.Times.dt.minute
    df = df.sort_values('Times')

    return(df)

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