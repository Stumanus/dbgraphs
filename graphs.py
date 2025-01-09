import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

'''Extract data from ~/HealthData/DBs/garmin_summary.db
    Sleep data is in ~/HealthData/DBs/garmin.db'''

conn = sqlite3.connect('/home/stu/HealthData/DBs/garmin_summary.db')
q1 = 'SELECT day, hr_avg, rhr_avg, inactive_hr_avg, intensity_time, moderate_activity_time, \
        vigorous_activity_time, stress_avg, calories_avg, calories_bmr_avg, calories_active_avg, \
        calories_consumed_avg, calories_goal, activities_calories FROM days_summary \
        WHERE day BETWEEN DATETIME("now","-8 days") AND DATETIME("now","-1 days");'

conn2 = sqlite3.connect('/home/stu/HealthData/DBs/garmin.db')
q2 = 'SELECT day,total_sleep,deep_sleep,light_sleep,rem_sleep,awake,avg_stress,score \
        FROM sleep WHERE day BETWEEN DATETIME("now","-8 days") AND DATETIME("now","-1 days");'

#Import data into pandas and do some preprocessing
df1 = pd.read_sql_query(q1,conn)
df2 = pd.read_sql_query(q2,conn2)
garmin_df = pd.merge(df1,df2,how='inner',on='day')
garmin_df.fillna(value=0, inplace=True)
time_cols = garmin_df.select_dtypes(include=['object']).iloc[:,1:].columns
for x in time_cols:
    garmin_df[x] = pd.to_timedelta(garmin_df[x])
    garmin_df[x] = garmin_df[x].apply(lambda x: x.total_seconds() / 3600)
garmin_df['day'] = pd.to_datetime(garmin_df['day'])

#Create 2x2 figure with Sleep, Calories, Excercise, Heart charts 
fig, axes = plt.subplots(2,2,figsize=(10,8))

#Sleep Chart
sleep_df = garmin_df[['day','total_sleep','deep_sleep','light_sleep','rem_sleep','awake']]
offset = timedelta(hours=3)
multiplier = 0
for col in sleep_df.iloc[:,1:].columns:
    spacing = (offset * multiplier) - offset
    axes[0,0].bar(sleep_df['day']+spacing,sleep_df[col],width=.1,label=col)
    multiplier+=1
axes[0,0].set_ylabel('Hours')
axes[0,0].set_title('Sleep')
#axes[0,0].set_ylim(top=(sleep_df.iloc[:,1:].max().max()*1.2))
axes[0,0].legend()

#Activity Chart
activity_df = garmin_df[['day','moderate_activity_time','vigorous_activity_time']]
activity_df.iloc[:,1:] = activity_df.iloc[:,1:].apply(lambda x: x*60)
for row in activity_df.iterrows():
    x = row[1].iloc[0]
    y = row[1].iloc[1:]
    bottom = 0
    colors = ['g','b','r']
    for i,feature in enumerate(y):
        axes[0,1].bar(x,feature,label=activity_df.columns[i+1],bottom=bottom,color=colors[i])
        bottom+=feature
axes[0,1].set_ylabel('Minutes')
axes[0,1].set_title('Activity')
axes[0,1].legend(activity_df.columns[1:])

#Calories Chart
calories_df = garmin_df[['day','calories_avg','calories_bmr_avg','calories_active_avg','calories_consumed_avg','calories_goal','activities_calories']]
for row in calories_df.iloc[:,1:].columns:
    axes[1,0].plot(calories_df['day'],calories_df[row],label=row)
axes[1,0].set_ylabel('Calories')
axes[1,0].set_title('Calories In/Out')
axes[1,0].legend()

#Heart Chart
#axes[1,1].plot(stress_ra.keys(),stress_ra.values(),label='Stress', color='#0078D7')
#axes[1,1].set_ylabel('Score')
#axes[1,1].set_title('Heart')
#axes[1,1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y'))
#axes[1,1].legend()

plt.tight_layout()
plt.show()
