# A Yahoo API Module
# 
# Yahoo has a couple constructs with their API:
#
# ~~~Collections~~~
# A Set of Resources. Can be used to gather multiples of resource types using filters.
#
# ~~~Sub-resources~~~
# Resources can have sub-resources, and only certain resource types will be valid sub-resources
# for certain parent resource types.
# 
# ~~~Resources~~~
# Game
#  API: https://fantasysports.yahooapis.com/fantasy/v2/game/{game_key}
#  In our context, {game_key} = 'nhl'
#
# League
#  API: https://fantasysports.yahooapis.com/fantasy/v2/league/{game_key}.{league_key}
#  {league_key} ~ l.{league_id}
#  Endpoints:
#	/settings
#	/standings
#	/scoreboard
#	/teams
#	/players[;player_keys={player_key}]
#
# Team
#  API: https://fantasysports.yahooapis.com/fantasy/v2/team/{game_key}.{league_key}.{team_key}
#  {team_key} ~ t.{team_id}
#  Endpoints:
#	/matchups
#	/stats;type=season
#	/stats;type=date;date=2018-11-01
#
# Roster
#  API: https://fantasysports.yahooapis.com/fantasy/v2/team/{game_key}.{league_key}.{team_key}/roster
#  Endpoints:
#	/players
#
# Player
#  API: https://fantasysports.yahooapis.com/fantasy/v2/player/{game_key}.{player_key}
#  {player_key} ~ p.{player_id}
#  Endpoints:
#	/stats
#   * can also get using the nested in league call seen above under League
#
# ~~~Notes~~~
#  More resources exist, but this covers most that are useful for analysis.
import requests
import re
import xml.etree.ElementTree as ET

# PRIVATE METHODS: (if this is a thing in python...)

def Request(Oauth, FullUrl=""):
	response = Oauth.session.get(FullUrl)
	if response.status_code is not 200:
		raise Exception("Request failed with code: %s\n%s" % (response.status_code, response.text))
	return ET.fromstring(response.text)

def XmlToResource(Xml, Obj=None):
	if Obj is None:
		Obj = {}
	for ele in Xml:
		tag = re.sub(r'^\{.*\}','',ele.tag)
		if len(ele) > 0:
			temp = Obj.get(tag)
			if temp is not None:
				if isinstance(temp, dict):
					Obj[tag] = []
					Obj[tag].append(temp)
				Obj[tag].append(XmlToResource(ele))
			else:
				Obj[tag] = XmlToResource(ele)
		else:
			Obj[tag] = ele.text
	return Obj

class YahooApi:

	def __init__(self, oauth=None, league_id='', game_key='nhl', root_url="https://fantasysports.yahooapis.com/fantasy/v2"):
		if oauth is None:
			raise Exception("Must pass an oauth arg")
		self.oauth = oauth
		self.league_id = league_id
		self.game_key = game_key
		self.root_url = root_url

	def game(self, endpoint=""):
		target = "/game/%s%s" % (self.game_key, endpoint)
		return XmlToResource(Request(self.oauth, self.root_url + target))

	def league(self, endpoint=""):
		target = "/league/%s.l.%s%s" % (self.game_key, self.league_id, endpoint)
		return XmlToResource(Request(self.oauth, self.root_url + target))

	def team(self, endpoint="", team_id=None):
		if team_id is None:
			raise Exception("Must pass team_id")
		target = "/team/%s.l.%s.t.%s%s" % (self.game_key, self.league_id, team_id, endpoint)
		return XmlToResource(Request(self.oauth, self.root_url + target))

	# player(...)
	# 
	# Get Player
	# ...
	def player(self, endpoint="", player_id=None):
		if player_id is None:
			raise Exception("Must pass a player_id")
		target = "/player/%s.p.%s%s" % (self.game_key, player_id, endpoint)
		return XmlToResource(Request(self.oauth, self.root_url + target))

	# lplayers(..)
	#
	# Get League Players
	# 
	# This API will return a list of players from the league.
	#
	# Accepts:
	#  start : [int >= 0] allows you to page through data with separate calls
	#  count : [int > 0] number of players to return
	#  position : [string] e.g. C, LW, RW, D, F, G, P(?)
	#  status : [string] e.g. A - all, FA - free agents, W - waivers, T - taken
	#  search : [string] search by name e.g. "smith"
	#  sort : [string] e.g. {stat_id}, NAME, OR - overall rank, AR - actual rank, PTS - fantasy points
	#  sort_type : [string] e.g. season(*), date(**), lastweek, lastmonth
	#  (*)sort_season : [string] the year, e.g. "2018"
	#  (**)sort_date : [date] YYYY-MM-DD e.g. 2018-10-10
	def lplayers(self, start=0, count=None, position=None, status=None, search=None, sort=None, sort_type=None, sort_season=None, sort_date=None):
		target = "/league/%s.l.%s/players;start=%s" % (self.game_key, self.league_id, start)
		if count is not None:
			target += ";count=%s" % count
		if position is not None:
			target += ";position=%s" % position
		if status is not None:
			target += ";status=%s" % status
		if search is not None:
			target += ";search=%s" % search
		if sort is not None:
			target += ";sort=%s" % sort
			if sort_type is not None:
				target += ";sort_type=%s" % sort_type
				if sort_season is not None:
					target += ";sort_season=%s" % sort_season
				elif sort_date is not None:
					target += ";sort_date=%s" % sort_date
		# return the resource list:
		resource = XmlToResource(Request(self.oauth, self.root_url + target))
		players = resource['league']['players']['player']
		return players














