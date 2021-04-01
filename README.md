# Showcase FF
Fantasy Football Dashboard that scrapes data from multiple sites and organizes the data.

The scraping functionality is not available since it requires username and password for the specific sites it is spraping.

The demo is currently currently grabbing a subset of data and using it to show the front end capabilities.
Here is a live demo of the app _______.

# Dependency Install

I chose to pipenv to manage the environment needed for the project since Heroku works flawlessly with pipenv.

First clone the repo 

`git clone  https://github.com/SuperChargedNeutron/Showcase_FF`

then cd Showcase_FF

`pipenv install`

if you dont have pipenv-> pip install pipenv

then we need to point flask to thedirectory where our app iinstance is located, namely the DFS folder.
You can do this by running the follwoing commands or setting all the variables in a .env file in the root directory of the repo. 

`export FLASK_APP=DFS`

`export SECRET_KEY=********`

`export MONGODB_URI=mongo+srv://user:password@host:port/db`


now we are ready to run the app 

`flask run`

