#     FireOwl - HackMIT project - 9/20/2020
A Project that shows a live dashboard of all the fires in the United States

Created by:
    Allen Lin
    Ben Carter
    Krishna Ramani 
    Sahil Khan

To run, install the following requirements:
    bottle
    mysql.connector
    urllib3
    gunicorn
      
Edit the below to adjust the port that is served.
PORT_TO_SERVE = 8012    
Edit the below to adjust where the website files are served. These files are included with the problem
webfiles = "your_path_here"


Then, to run, simply type 'python3 v3.py' 


Welcome to FireOwl!

FireOwl is an online service that allows users to submit locations of fires that they have seen. In addition, they can also view fires submitted by other users around the world, as well as government-reported fires that we gather data from. Finally, we also pull wind data from online weather APIs for each of the fires submitted, which can be viewed on the prediction mode of the website to see areas where active wildfires could be growing due to wind speed increases.
