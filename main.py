from yahoo_oauth import OAuth2
from yahoo_api import YahooApi
import json
import redis
oauth = OAuth2(None, None, from_file='oauth.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()

league_file = open("league_info.json")
league_info = json.loads(league_file.read())

yahoo = YahooApi(oauth=oauth, league_id=league_info['league_id'], game_key=league_info['game_key'])

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
r.flushall() # if redis is configured to persist, this will throw an error

## set up the team map
teams = yahoo.league("/teams")
teams = teams['league']['teams']['team']
for team in teams:
	team_id = team['team_id']
	manager_id = team['managers']['manager']['manager_id']
	mappings = {
		"manager_id" : manager_id,
		"name" : team['name'],
		"logo" : team['team_logos']['team_logo']['url']
	}
	r.hmset("team:%s" % team_id, mappings)
	r.lpush("teams", team_id)

# Setup the stat categories map
stats = yahoo.league("/settings")
stats = stats['league']['settings']['stat_categories']['stats']['stat']
for stat in stats:
	if stat.get('is_only_display_stat'):
		continue
	stat_id = stat['stat_id']
	mappings = {
		"display_name" : stat['display_name'],
		"name" : stat['name'],
		"position_type" : stat['position_type']
	}
	r.hmset("stat:%s" % stat_id, mappings)
	r.lpush("stat_categories", stat_id)

# build totals data and stat rank dat
standings = yahoo.league("/standings")
standings = standings['league']['standings']['teams']['team']
for standing in standings:
	team_id = standing['team_id']
	team_stats = standing['team_stats']['stats']['stat']
	for team_stat in team_stats:
		stat_id = team_stat['stat_id']
		r.set("totals:team:%s:stat:%s" % (team_id, stat_id), team_stat['value'])
		r.zadd("stat_rank:%s" % stat_id, team_id, team_stat['value'])

# compile team rank data
for team_id in r.lrange('teams', 0, r.llen('teams')):
	for stat_id in r.lrange('stat_categories', 0, r.llen('stat_categories')):
		#r.lpush("team_rank:team:%s" % (team_id), r.zrank("stat_rank:%s" % stat_id, team_id)) # rankplot.py
		if r.hget("stat:%s" % stat_id, "display_name") == "GAA":
			r.zadd("team_rank:team:%s" % (team_id), r.hget("stat:%s" % stat_id, "display_name"), r.zrevrank("stat_rank:%s" % stat_id, team_id))
		else:
			r.zadd("team_rank:team:%s" % (team_id), r.hget("stat:%s" % stat_id, "display_name"), r.zrank("stat_rank:%s" % stat_id, team_id))

# Get the team week stats:
team_ids = r.lrange("teams", 0, -1)
weeks = range(1,7)
for tid in team_ids:
	for week in weeks:
		team_stats = yahoo.team(endpoint="/stats;type=week;week=%s" % week, team_id=tid)
		for stat in team_stats['team']['team_stats']['stats']['stat']:
			r.set("team_stat:week:%s:team:%s:stat:%s" % (week, tid, stat['stat_id']), stat['value'])

for week in weeks:
	league_scoreboard = yahoo.league(endpoint="/scoreboard;week=%s" % week)
	for matchup in league_scoreboard['league']['scoreboard']['matchups']['matchup']:
		r.set("matchup:week:%s:team:%s" % (week, matchup['teams']['team'][0]['team_id']), matchup['teams']['team'][1]['team_id'])
		r.set("matchup:week:%s:team:%s" % (week, matchup['teams']['team'][1]['team_id']), matchup['teams']['team'][0]['team_id'])
