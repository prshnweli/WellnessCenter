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
gc = pygsheets.authorize(service_file='keys/creds.json')

# Open google sheet that's been shared with the email in the json file
sheet = gc.open('All Wellness Center Check-Ins')

# Select first sheet
wks = sheet.Errors

# Read data
df = wks.get_as_df(has_header=True)
print(df)
