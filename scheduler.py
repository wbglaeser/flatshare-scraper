#-------------------------------------
# Import Modules
#-------------------------------------
from datetime import datetime
from threading import Timer
import run_script
import emailer

x=datetime.today()
y=x.replace(day=x.day, hour=x.hour, minute=3, second=0, microsecond=0)
delta_t=y-x

secs=delta_t.seconds+1

#-------------------------------------
# Define the function
#-------------------------------------
def execute_script():
    run_script.main_func()
    emailer.main_func()

def schedule_script():
    # Set time for next scraper
    t_ = Timer(60*60, schedule_script)
    t_.start()
    print('Scraper is on!')
    try:
        execute_script()
        print('timer is sleeping')
    except:
        t_2 = Timer(60*10, execute_script)
        t_2.start()
        print('Did not work last time around. so giving it another try')
    # Send updaets about time till next scrape
    de = 5
    t1 = datetime.today()
    while True:
        t2 = datetime.today()
        diff = t2-t1
        if diff.seconds > 300:
            print('{} minutes since the last scrape'.format(de))
            de += 5
            t1 = t2
            if de > 55:
                break
        
#-------------------------------------
# Start the script
#-------------------------------------
t = Timer(secs, schedule_script)
t.start()
