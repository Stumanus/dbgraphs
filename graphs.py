import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

conn = sqlite3.connect('/home/stu/HealthData/DBs/garmin.db')
c = conn.cursor()

times = list()
vals = list()

c.execute('SELECT * FROM stress;')
cutoff_dt = datetime.now() - timedelta(days=1)
for row in c.fetchall():
    time = datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S.%f')
    if time > cutoff_dt:
        times.append(row[0])
        vals.append(row[1])


plt.plot(times,vals)
plt.show()
