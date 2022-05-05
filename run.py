#imports
import pandas as pd
import pyodbc
import numpy as np
from datetime import *
import csv
import openpyxl
import pygsheets
import os
import config
gc = pygsheets.authorize(service_file='keys/creds.json') # Might need to recreate this json file

# Open google sheet that's been shared with the email in the json file
sheet = gc.open('All Wellness Center Check-Ins')

# Select first sheet
wks = sheet[0]

# Read data
df = wks.get_as_df(has_header=True)

# Comes up as floats if left blank. Shouldn't be blank right?
df['School Number'] = df['School Number'].fillna(0)
df['School Number'] = df['School Number'].astype(int)

# Add date and time column.
df['Date'] = pd.to_datetime(df['Submission Date']).dt.date
df['Time'] = pd.to_datetime(df['Submission Date']).dt.time

# Change datatype from object to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Subset only records from today
tdy = df.loc[df['Date'] == pd.to_datetime('today').normalize()]
#tdy = df.loc[df['Date'] == pd.to_datetime('4/27/2022').normalize()]

def run():
    global tdy

    tdy = tdy.copy(deep = True) # Removes the replace warning.

    # Create code column
    # If time is =< than 9am = WBS
    # If time is > 9am and =< 11:15 = WBR
    # If time is => 11:20 and =< 2:00 = WL
    # If time is => 2:30 = WAS

    def code(row):
        if row['Time'] <= pd.to_datetime('9:00:00').time():
            return 'WBS'
        elif row['Time'] > pd.to_datetime('9:00:00').time() and row['Time'] <= pd.to_datetime('11:15:00').time():
            return 'WBR'
        elif row['Time'] > pd.to_datetime('11:15:00').time() and row['Time'] <= pd.to_datetime('14:00:00').time():
            return 'WL'
        elif row['Time'] > pd.to_datetime('14:00:00').time():
            return 'WAS'
        else:
            return ''

    tdy['cd'] = tdy.apply(lambda row: code(row), axis = 1)

    # Check if Student ID exists in db
    # start connection to database
    conn = pyodbc.connect('Driver={SQL Server};'
    'Server='+config.Server+';'
    'Database='+config.Database+';'
    'UID='+config.UID+';'
    'PWD='+config.PWD+';'
    )

    # Pull all student IDs
    sidquery = "SELECT DISTINCT(STU.ID) FROM STU WHERE STU.TG = '' AND STU.DEL = 0 AND STU.SC IN (2,6,8,9,10,11,12,15,20,21,30,31,32)"
    stuids = pd.read_sql_query(sidquery, conn)

    # All records with ID not in Aeries
    errors = tdy[~tdy['Student ID Number'].isin(stuids['ID'])]
    errors = errors.copy(deep = True)

    # Add School Names
    school = {
        2:'El Toro',
        6:'Los Paseos',
        8:'Nordstrom',
        9:'Paradise',
        10:'SMG',
        11:'Walsh',
        12:'Barrett',
        15:'JAMM',
        20:'Britton',
        21:'Murphy',
        30:'Central',
        31:'Live Oak',
        32:'Sobrato'
    }

    errors['School'] = errors['School Number'].map(school)
    # All valid records
    upload = tdy[tdy['Student ID Number'].isin(stuids['ID'])]
    upload = upload.copy(deep = True)


    # Add Max SQ
    sqquery = "SELECT SCHK.ID, MAX(SCHK.SQ) AS 'MAXSQ' FROM SCHK GROUP BY SCHK.ID"
    sq = pd.read_sql_query(sqquery, conn)

    # Create in spreadsheet SQ
    upload['dailysq'] = upload.groupby('Student ID Number').cumcount() + 1

    # merge
    upload = pd.merge(upload, sq, how='left', left_on = 'Student ID Number', right_on = 'ID')
    upload['MAXSQ'] = upload['MAXSQ'].fillna(0)
    upload['MAXSQ'] = upload['MAXSQ'].astype(int)

    # Add both SQs
    upload['SQ'] = upload['dailysq'] + upload['MAXSQ']

    # Change from 24 hr to 12 hr
    upload['Time'] = upload['Time'].astype(str)
    upload['Time'] = pd.to_datetime(upload['Time']).dt.strftime("%I:%M %p")

    final = upload[['Student ID Number', 'SQ', 'Date', 'cd', 'Time', 'Submission Date']]
    final.columns = ['ID', 'SQ', 'DT', 'CD', 'CO', 'DTS']

    print(final)
    final.to_csv('upload.csv', index = False)
    # Upload into SQL
    # cursor = conn.cursor()
    #
    # for index, row in final.iterrows():
    #     cursor.execute("INSERT INTO DST21000MorganHill.dbo.SCHK (ID, SQ, DT, CD, CO, DTS) values(?,?,?,?,?,?)", row.ID,row.SQ,row.DT,row.CD,row.CO,row.DTS
    # )
    #
    # conn.commit()
    # cursor.close()
    conn.close()

    # Export errors into csv
    if errors.empty:
        print('No Errors')
    else:
        errors.to_csv('errors.csv', mode='a', index=False, header=False)
        errs = pd.read_csv('errors.csv', engine='python')
        err_sheet = sheet[1] # Errors is second sheet
        err_sheet.set_dataframe(errs, 'A1')

#If there are no records for today then don't run the script.
if tdy.empty:
    print('No records for today')
else:
    run()
