Script that adds all your due assignments to the google calendar and to the apple calendar(in iOS) if you allow google calendar to access calendar app in your phone

Steps to run the script:<br />
1). Download the files due_assigns_reminder.py and credentials.json to a same directory<br />
2). Run the python script with python3<br />
3). Signin with the google in the pop up that appears with the account to which you want to add the events<br />
4). After successfully logging into google, return to the terminal window<br />
5). Provide your moodle credentials<br />
6). Wait for some time for the script to run<br />

After the script is run successfully, your due assignments would appear in terminal window, a csv file named reminder.csv and to the google calendar. Don't mess with the csv file or you may end up adding duplicate events to the calendar.

NOTE: The script would add all the due assignments of the courses that you're enrolled into moddle except for the courses like Modelling and Simulation.
