import json
import requests

import pandas as pd

import api_access
from bill_parser import BillParser

with requests.Session() as s:
    s.headers.update(api_access.HEADERS)

    print('讀取組態 Loading Configurations...')
    with open('config.json', 'r', encoding='utf8') as f:
        config = json.load(f)
    NATIONAL_ID = config["National_ID"]
    PASSWORD = config["Password"]
    B64P12CERT = config["b64P12Cert"]
    print('OK.')

    print('正在登入 Login...')
    status, r = api_access.login(s, NATIONAL_ID, PASSWORD)
    if status:
        print('OK.')
    else:
        raise RuntimeError(f'Failed. Reason: {r.reason}.')
    
    print('正在驗證憑證 Verifying certificates...')
    status, r = api_access.verify_CA(s, NATIONAL_ID, B64P12CERT)
    if status:
        print('OK.')
    else:
        raise RuntimeError(f'Failed. Reason: {r.reason}.')

    print('正在讀取可用日期 Loading available dates...')
    status, r = api_access.load_ebill_available_dates(s)
    if status:
        print('OK.')
    else:
        raise RuntimeError(f'Failed. Reason: {r.reason}.')

    bp = BillParser(r.text)
    
    available_dates = sorted(bp.parse_available_dates())
    selected_dates = None
    ebills = []

    while selected_dates is None:
        print('請輸入需要下載的日期區間，留空以下載所有電子對帳單 ' +\
               'Please input a range of dates you want to download. ' +\
               'Leave blank to download all ebills.')
        print(available_dates)
        starting_date = input(f'開始日期 Starting date:')
        ending_date = input(f'結束日期 Ending date:')

        if (len(starting_date), len(ending_date)) == (0, 0):
            start_end = (available_dates[0], available_dates[-1])
            selected_dates = available_dates

        elif starting_date in available_dates and ending_date in available_dates:
            # In case the user swaps starting & ending date.
            start_end = sorted([starting_date, ending_date])

            start_idx = available_dates.index(start_end[0])
            end_idx = available_dates.index(start_end[1])
            
            selected_dates = available_dates[start_idx:end_idx+1]
        else:
            print('日期輸入錯誤，請重新輸入 Invalid dates, please try again.')
            continue

        print(f'已選擇的日期 Selected dates: { ",".join(selected_dates)}')

    print('正在讀取電子對帳單 Loading ebills by selected dates...')
    for date in selected_dates:
        if len(date) == 6:
            status, r = api_access.load_ebill_by_month(s, date)
        else:
            status, r = api_access.load_ebill_by_date(s, date)
        if status:
            print(f'{date} OK.')
        else:
            raise RuntimeError(f'Failed. Reason: {r.reason}.')

        bp.renew(r.text)
        ebills.append(bp.parse_bill_tables(date))

    print('正在產生.xlsx檔 Generating .xlsx file...')
    # Build dataframes
    dataframes = {}
    for ebill_table in ebills:
        for key, value in ebill_table.items():
            if key in dataframes:
                dataframes[key]['data'].extend(value['data'])
            else:
                dataframes[key] = {
                    'headers': value['headers'], 'data': value['data']}

    writer = pd.ExcelWriter(f'{start_end[0]}-{start_end[1]}.xlsx', engine='xlsxwriter')

    for key, value in dataframes.items():
        df = pd.DataFrame(data=value['data'], columns=value['headers'])
        df.to_excel(writer, sheet_name=key)
    writer.save()
    print('OK.')