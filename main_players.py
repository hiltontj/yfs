# main players
from yahoo_oauth import OAuth2
from yahoo_api import YahooApi
import redis
oauth = OAuth2(None, None, from_file='oauth.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()

yahoo = YahooApi(oauth=oauth, league_id='35431', game_key="nhl")

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)

def routine():
	Start = raw_input("start: ") or 0
	Count = raw_input("count: ") or None
	Position = raw_input("position: ") or None
	Status = raw_input("status: ") or None
	Search = raw_input("search: ") or None
	Sort = raw_input("sort: ") or None
	SortType = raw_input("sort_type: ") or None
	SortSeason = raw_input("sort_season: ") or None
	SortDate = raw_input("sort_date: ") or None

	return yahoo.lplayers(start=Start, count=Count, position=Position, status=Status, search=Search, sort=Sort, sort_type=SortType, sort_season=SortSeason, sort_date=SortDate)

players = routine()