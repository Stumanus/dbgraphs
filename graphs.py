import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from matplotlib import rcParams
from datetime import datetime, timedelta

primary_color = "#0078D7"  # Home Assistant's default blue
background_color = "#202124"  # Dark mode background
grid_color = "#44474F"  # Subtle grid color
text_color = "#E8EAED"  # Light gray for primary text

rcParams.update({
    "axes.facecolor": background_color,  # Background of the axes
    "axes.edgecolor": text_color,  # Edge color of axes
    "axes.grid": True,  # Enable grid by default
    "grid.color": grid_color,  # Grid color
    "grid.linewidth": 0.5,  # Grid line width
    "axes.titlesize": 14,  # Title font size
    "axes.titleweight": "bold",  # Title weight
    "axes.labelsize": 12,  # Axis label font size
    "axes.labelcolor": text_color,  # Axis label color
    "xtick.color": text_color,  # X-axis tick color
    "ytick.color": text_color,  # Y-axis tick color
    "xtick.labelsize": 10,  # X-axis tick label size
    "ytick.labelsize": 10,  # Y-axis tick label size
    "font.family": "DejaVu Sans",  # Use a modern sans-serif font
    "figure.facecolor": background_color,  # Background of the figure
    "figure.edgecolor": background_color,  # Edge color of the figure
    "legend.facecolor": "#303134",  # Slightly lighter background for the legend
    "legend.edgecolor": grid_color,  # Legend border color
    "legend.fontsize": 10,  # Legend font size
    "lines.linewidth": 2,  # Default line width
    "lines.markersize": 6,  # Default marker size
    "text.color": text_color,  # Default text color
})
#Extract data from ~/HealthData/DBs/garmin.db
conn = sqlite3.connect('/home/stu/HealthData/DBs/garmin.db')
c = conn.cursor()

#Rolling avg stress
c.execute(f'SELECT * FROM stress WHERE timestamp >= (SELECT DATETIME("now","-7 day"));')
times = list()
vals = list()
rolling_avg_period=240
for row in c.fetchall():
    time = datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S.%f')
    times.append(time)
    vals.append(row[1])
#Compute rolling avg, append to dict
vals = np.convolve(vals, np.ones(rolling_avg_period) / rolling_avg_period, mode='valid')
times = times[-len(vals):]
stress_ra = {time:val for time,val in zip(times,vals)}

#Sleep score and total sleep daily
c.execute(f'SELECT * FROM sleep WHERE day >= (SELECT DATETIME("now","-7 day"));')
sleep_totals = dict()
sleep_score = dict()
for row in c.fetchall():
    day = datetime.strptime(row[0],'%Y-%m-%d')
    start = datetime.strptime(row[1],'%Y-%m-%d %H:%M:%S.%f')
    end = datetime.strptime(row[2],'%Y-%m-%d %H:%M:%S.%f')
    total_sleep = datetime.strptime(row[3],'%H:%M:%S.%f')
    total_sleep = float(total_sleep.hour + float(total_sleep.minute / 60))
    deep_sleep = row[4]
    light_sleep = row[5]
    rem_sleep = row[6]
    awake = row[7]
    sleep_stress = row[9]
    score = row[10]
    sleep_score[day] = score
    sleep_totals[day] = total_sleep

#Moderate and Vigorous activity minutes daily
moderate_activity_totals = dict()
vigorous_activity_totals = dict()
c.execute('SELECT day,moderate_activity_time, vigorous_activity_time FROM daily_summary WHERE day >= \
        (SELECT DATETIME("now","-7 day"));')
for row in c.fetchall():
    day = datetime.strptime(row[0],'%Y-%m-%d')
    moderate_time = datetime.strptime(row[1],'%H:%M:%S.%f')
    moderate_time = (moderate_time.hour * 60) + moderate_time.minute
    vigorous_time = datetime.strptime(row[1],'%H:%M:%S.%f')
    vigorous_time = (vigorous_time.hour * 60) + vigorous_time.minute
    moderate_activity_totals[day] = moderate_time
    vigorous_activity_totals[day] = vigorous_time

conn.close()

#Extract data from ~/HealthData/DBs/garmin_summary.db
conn = sqlite3.connect('/home/stu/HealthData/DBs/garmin_summary.db')
c = conn.cursor()

#Net Calories Consumed daily
net_cals_consumed = dict()
c.execute('SELECT day, calories_active_avg, calories_consumed_avg FROM days_summary \
        WHERE day >= (SELECT DATETIME ("now","-7 day"));')
for row in c.fetchall():
    print(row)



plt.figure(figsize=(8, 4))
plt.plot(stress_ra.keys(),stress_ra.values(), label='stress', color="#0078D7")
plt.bar(sleep_totals.keys(),sleep_totals.values(), label='total_sleep',color='g')
plt.scatter(sleep_score.keys(),sleep_score.values(), label='sleep_score', color='r')
plt.bar(moderate_activity_totals.keys(),moderate_activity_totals.values(), label='moderate_total', color='b')
plt.legend()
plt.show()
