# PulseFi?

<img src="logo.png" alt="logo" width="200"/>

PulseFi uses music and health APIs to study the effect of music on human physiology, allowing users to control their body and mind through music selection based on data analysis.

# How to use PulseFi?

vist the website: https://pulse-fi.herokuapp.com/

Note:
    only optimized for desktop use, mobile use is not recommended

there is extensive setup required to deploy the app between the setting up the postgres database and setting up the developer accounts for fitbit and spotify. Instead of providing the extensive list of environment variables and account information, the app is deployed on heroku and can be used by visiting the website.

upon visiting the website click on the login button in the top left hand corner, click the "login as guest" button to use the credientials of Matthew Nann. This will allow you to use the app without needing to own a fitbit or spotify account. If you would like to use your own fitbit or spotify account, can register an account with PulseFi by clicking the "register" button in the top left hand corner. Once logged in, navigate to the dashboard page to see all data.

# STACK
- python (3.9.16)
- flask - python web framework, boilerplate code from flask-login was used to shell out the login and registration pages
- postgres database
- dash - web based data visualization (integrated into flask app)
- html, css, javascript - limited use with flask
- heroku - cloud platform, used to automatically deploy the most recently commit on main branch

## APIs
the user can use either fitbit or oura ring depending on what consumer health tracking device they own
- spotify API - music data
- oura ring API - health data
- fitbit API - health data

## dashboard page

### selecting user's spotify playlist to be used in each mode
1. select between Sleep, Exercise, Relax, Work with drop down menu
2. select a playlist from the user's spotify account

### once updated, the playlist will be used in the selected mode
3. start a mode, which cause music from selected playlists to be played on the user's spotify account (if guest account, the music will be played on the guest account, if registered account, the music will be played on the user's spotify account)

### data analysis
4. select the date range to view the played music and heart rate data
5. interact with the parallel coordinate graph by dragging along the a vertical axis to select a range of songs to view, double click to remove the selection

<img src="dashboard.png" alt="dashboard" width="500"/>

## user stories

1. As a user, I want to be able to access my data from oura ring so that I can see all of my available health data in one central space.
    - https://tasks.office.com/Clemson.onmicrosoft.com/Home/Task/1-_QwTmd10em2dU1ju-kPmQAI2n6?Type=TaskLink&Channel=Link&CreatedTime=638179461996610000
2. As a user, I would like to see the characteristics of the music I listen
    - https://tasks.office.com/Clemson.onmicrosoft.com/Home/Task/e_frgHpHuU2Ow7jbnOv9F2QAE6vs?Type=TaskLink&Channel=Link&CreatedTime=638179463461230000
3. As a user, I would like to specified the music that is allowed to be recommended
    - https://tasks.office.com/Clemson.onmicrosoft.com/Home/Task/0Q8X4D777UGFjMXznlQc1WQAIbou?Type=TaskLink&Channel=Link&CreatedTime=638179464471050000
4. As a user, I want to see my music playlists so that I can always have the option to choose my playlist manually.
    - https://tasks.office.com/Clemson.onmicrosoft.com/Home/Task/DSh2OicW_0WS7JnFG1dsIGQAPxQi?Type=TaskLink&Channel=Link&CreatedTime=638179464537400000
5. As a user, I would like to login into a website to access my data
    - https://tasks.office.com/Clemson.onmicrosoft.com/Home/Task/8Gwq6zMpWkutLNR53hkdAmQADTxa?Type=TaskLink&Channel=Link&CreatedTime=638179464684620000
6. As a user, I want to be able to access my data from fitbit so that I can see all of my available health data in one central space.
    - https://tasks.office.com/Clemson.onmicrosoft.com/Home/Task/y80R81D4QUar_ADXKlurMWQACn6d?Type=TaskLink&Channel=Link&CreatedTime=638179464957360000