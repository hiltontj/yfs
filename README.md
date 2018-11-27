# yfs
Yahoo! Fantasy Sports API Exploration

## Getting Started

To use the code in this repo, you will need to have a valid Yahoo! Fantasy Sports account and be participating in a league. This code is meant for the Yahoo! Fantasy Hockey, but could probably be adapted easily to the other sports. All of the code here is written in Python. There are several Python dependancies which you will need to have installed:

## Dependancies:

* [yahoo_oauth](https://pypi.org/project/yahoo_oauth/)
* [redis](https://pypi.org/project/redis/)
* [numpy](http://www.numpy.org/)
* [pandas](https://pandas.pydata.org/)
* [matplotlib](https://matplotlib.org/)
* [seaborn](https://seaborn.pydata.org/)

### yahoo_oauth

This is a great library for handling the web requests to Yahoo! using OAuth. It also handles the initialization of your credentials (access and refresh tokens, etc.). Check the link above for more details on how to initialize. In summary, you will need to create a JSON file that contains the following information:

```
{
   "consumer_key": "my_very_long_and_weird_consumer_key",
   "consumer_secret": "my_not_that_long_consumer_secret"
}
```
And reference it by location in the **from_file** argument to the **OAuth2(...)** call (see main.py). The **consumer_key** and **consumer_secret** can be generated by going to the **Create Application** page [here](https://developer.yahoo.com/apps/create/). You will need to sign into your account to generate it. Make sure to choose **Installed Application**, and to give permissions to **Fantasy Sports**, the rest is not required.

Once you have initialized your oauth.json file, the first time you run main.py or main_players.py (either uses the yahoo_oauth), you will trigger the redirect which takes to Yahoo where you enter your login credentials. After doing so, your JSON file will be updated with the access token and refresh token, and whatever else it needs to make requests seemlessly with the Yahoo API.

### redis

The data store used throughout these scripts is Redis. Visit [the redis page](https://redis.io/topics/quickstart) for more information on how to get a redis server running on your local machine. It will need to be running in order to execute the scripts in this repo.

### numpy, pandas, matplotlib, seaborn

These libraries are all used together to perform visualizations. Check out their pages linked above for more info on each.

## Using the Code

There are two types of scripts in this repo: data collection, and data visualization. Currently, the main.py script is meant to collect league and team data, while the main_players.py script is meant for collecting player data. The two visualization scripts are rankplot.py and opponant_pivot.py.

### yahoo_api.py

This is a class defined for getting and parsing resources from the Yahoo! API. It contains a set of methods, one for each API of interest.


