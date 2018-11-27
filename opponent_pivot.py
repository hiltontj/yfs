import redis
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
sns.set(style="white")

# Compile the pivot table, lol
week = '6'
cols = ['TEAM', 'OPPONENT', 'score']
team_ids = r.lrange("teams", 0, -1)
print team_ids
stat_ids = r.lrange("stat_categories", 0, -1)
Nteams = r.llen("teams")
#Data = np.empty((Nteams, Nteams))
Data = np.empty((((Nteams - 1) * Nteams), 3))
Data[:] = 0
TotalPointsAvailable = 28
Row = 0
team_names = []
actuals = []
for i in range(0, Nteams):
	team_names.append(r.hget('team:%s' % team_ids[i], "name"))
	faced = r.get("matchup:week:%s:team:%s" % (week, team_ids[i]))
	faced_ind = [a for a,b in enumerate(team_ids[::-1]) if b == faced]
	print team_ids[i], faced, faced_ind
	actuals.append((faced_ind[0], Nteams - (i+1)))
	for j in range(i + 1, Nteams):
		total = 0
		for sid in stat_ids:
			mine = float(r.get("team_stat:week:%s:team:%s:stat:%s" % (week, team_ids[i], sid)))
			theirs = float(r.get("team_stat:week:%s:team:%s:stat:%s" % (week, team_ids[j], sid)))
			isPM = r.hget("stat:%s" % sid, "display_name") == "+/-"
			diff = 0
			if isPM:
				if mine > theirs:
					diff = 1
				elif mine < theirs:
					diff = -1
			else:
				diff = mine - theirs
			isGaa = r.hget("stat:%s" % sid, "display_name") == "GAA"
			if diff == 0:
				total+=1
			elif diff > 0 and not isGaa:
				total+=2
			elif diff < 0 and isGaa:
				total+=2
		Data[Row,:] = [team_ids[i], team_ids[j], total]
		Row += 1
		Data[Row,:] = [team_ids[j], team_ids[i], TotalPointsAvailable - total]
		Row += 1
		#Data[i,j] = total
		#Data[j,i] = TotalPointsAvailable - total



frame = pd.DataFrame(data=Data, columns=cols)
points = frame.pivot_table(index="TEAM", columns="OPPONENT", values="score")
f, ax = plt.subplots(figsize=(9, 6))
sns.heatmap(points, annot=True, linewidth=0.5, ax=ax, cmap="RdBu", vmin=0, vmax=28, cbar_kws={"ticks":[0,14,28]})
for actual in actuals:
	ax.add_patch(Rectangle(actual, 1, 1, fill=False, edgecolor='black', lw=3))
ax.set_yticklabels(team_names[::-1], rotation='horizontal', fontsize="10")
ax.set_xticklabels(team_names[::-1], rotation=45, ha='right', fontsize="10")
ax.set_title("Actual and Hypothetical\nMatchup Results for Week %s" % week, fontsize=12)
plt.tight_layout()
plt.show()
#plt.savefig("matchups_wk%s.pdf" % week)
