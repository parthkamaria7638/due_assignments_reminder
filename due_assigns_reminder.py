from __future__ import print_function
from bs4 import BeautifulSoup as soup
import requests as req
import csv
from datetime import date
import datetime
import sys
import subprocess
import pandas as pd
subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade","google-api-python-client","oauth2client"])
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
from getpass import getpass

monthToNum = {}

monthToNum["January"] = '01'
monthToNum["February"] = '02'
monthToNum["March"] = '03' 
monthToNum["April"] = '04'
monthToNum["May"] = '05'
monthToNum["June"] = '06'
monthToNum["July"] = '07'
monthToNum["August"] = '08'
monthToNum["September"] = '09'
monthToNum["October"] = '10'
monthToNum["November"] = '11'
monthToNum["December"] = '12'

today = date.today()

SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
	creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

def createEvent(course, assignment, start_date, start_time, end_date, end_time):
    calSummary = course + ": " + assignment
    startTime = start_date + 'T' + start_time
    endTime = end_date + 'T' + end_time
    event = {
		'summary': calSummary,
		'location': '',
		'description': '',
		'start': {
		'dateTime': startTime,
		  'timeZone': 'Asia/Calcutta',
		},
        'end': {
		'dateTime': endTime,
		  'timeZone': 'Asia/Calcutta',
		},
		'reminders': {
		  'useDefault': False,
		  'overrides': [
		    {'method': 'popup', 'minutes': 24*60},
		  ],
		},
	}	
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return event.get('id')

def convert24(str1): 
    if str1[-2:] == "AM" and str1[:2] == "12": 
        return "00" + str1[2:-2] 
    elif str1[-2:] == "AM": 
        return str1[:-2] 
    elif str1[-2:] == "PM" and str1[:2] == "12": 
        return str1[:-2] 
    else: 
        return str(int(str1[:2]) + 12) + str1[2:8]

def appendZero(str):
    if (int(str) < 10):
        return str.zfill(2)
    return str

def formatTime(str):
    arr = str.split()
    flag = arr[1]
    time = arr[0]
    time = time.split(":")
    if (int(time[0]) < 10):
        time[0] = time[0].zfill(2)
    newTime = time[0] + ":" + time[1] + ":00" + flag
    return newTime

def getEndTime(calendar_date, newTime):
    date = calendar_date + " " + newTime
    time = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return str(time + datetime.timedelta(seconds=60))

def getEndDateAndTime(calendar_date, newTime):
    date = calendar_date + " " + newTime
    time = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    tempStr = str(time + datetime.timedelta(seconds=60))
    arr = tempStr.split()
    endDate = arr[0]
    endTime = arr[1] + "+05:30"
    return [endDate, endTime]

def deleteEventIfAlreadyExists(CSVDATA, TITLE):
    for i in range(len(CSVDATA)):
        if (CSVDATA["Course and Assignment"][i] == TITLE):
            eventId = CSVDATA["EventId"][i]
            try:
                event = service.events().get(calendarId='primary', eventId=str(eventId)).execute()
                print("Event was already present in the calendar. Updating it...")
                service.events().delete(calendarId='primary', eventId=eventId).execute()
                return
            except:
                print("Event wasn't present in the calendar. Adding it to the calendar...")
                return

    print("Event wasn't present in the calendar. Adding it to the calendar...")
    return            

def scrapData(username, password):
    try:
        data =pd.read_csv('reminder.csv')
    except:
        data = []
    s = req.session()
    r1 = s.get("https://courses.daiict.ac.in")
    r2 = s.post("https://courses.daiict.ac.in/login/index.php", 
    {'username': username, 'password': password},
    headers = {"Version": 'HTTP/1.1'})
    r3 = s.get("https://courses.daiict.ac.in/my/")


    r3_soup = soup(r3.text, "html.parser")
    course_list = r3_soup.find_all(id="course_list")
    courses = course_list[0].find_all(class_="box coursebox")

    csvData = []
    count = 1;
    csvData.append(["Course and Assignment", "Day", "Date", "Time", "Time Left(in days)", "EventId"])

    print('\033[1m')
    print("---------------------")
    print("Upcoming Submissions:")
    for i in range(len(courses)):
        title = courses[i].find(class_="title").get_text()
        assig = courses[i].find_all(class_="assignment overview")
        assig.extend(courses[i].find_all(class_="assign overview"))
        for j in range(len(assig)):
            assignment_title = assig[j].select("div a")[0].get_text()
            due_date = assig[j].find(class_="info").get_text()
            due_date = due_date[10:len(due_date)]
            [day, date_, time] = due_date.split(",")
            start_time = convert24(formatTime(time))
            [dateNum, dateMonth, dateYear] = date_.split()
            future_date = date(int(dateYear), int(monthToNum[str(dateMonth)]), int(dateNum))
            start_calendar_date = dateYear + "-" + monthToNum[str(dateMonth)] + "-" + appendZero(dateNum)
            [end_calendar_date, end_time] = getEndDateAndTime(start_calendar_date, start_time)
            start_time = start_time + "+05:30"
            time_left = (future_date-today).days
            if (future_date-today).days >= 0:
                print(str(count)+").")
                print("     Course: "+ str(title))
                print("     Title: "+str(assignment_title))
                print("     Due Date: "+str(due_date))
                print("     Time Left: "+str(time_left)+" days")
                deleteEventIfAlreadyExists(data, title + " " + assignment_title)
                id = createEvent(title, assignment_title, start_calendar_date, start_time, end_calendar_date, end_time)
                csvData.append([title + " " + assignment_title, day, date_, time, time_left, id])
                count = count + 1
    print("---------------------")
    print('\033[0m')
        

    with open('reminder.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()

def getCredentials():
    print("Enter your moodle username: ")
    username = input()
    print("Enter your moodle password: ")
    password = getpass()
    scrapData(username, password)

getCredentials()
