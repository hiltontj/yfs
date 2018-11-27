import redis
import numpy as np
import pandas as ps
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
sns.set(style="darkgrid")
sns.set(font_scale=0.5)

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)

Ncategories = r.llen('stat_categories')
stat_ids = r.lrange('stat_categories', 0, Ncategories)
stats_index = []
Nteams = r.llen('teams')
team_ids = r.lrange('teams', 0, Nteams)
teams = []

#f, axes = plt.subplots(4,3)
plt.figure(figsize=(20,10))
#ylbls = map(str, range(10,0,-1))
Palettes = ['YlGnBu_r']
i = 1
for tid in team_ids:
	teams.append(r.hget('team:%s' % tid, 'name'))
	stat_labels = r.zrevrange('team_rank:team:%s' % tid, 0, -1)
	scores = np.empty((1,Ncategories))
	rating = 0
	j = 0
	for lbl in stat_labels:
		scores[0,j] = r.zscore('team_rank:team:%s' % tid, lbl) + 1
		rating += scores[0,j]
		j += 1
	rating = rating
	print(rating)
	data = ps.DataFrame(scores, columns=stat_labels)
	plt.subplot(4,3,i)
	thisplot = sns.barplot(data=data, palette=Palettes[i % len(Palettes)])
	thisplot.set_ylim(0,10)
	#thisplot.set_xlim(-1,14)
	thisplot.yaxis.set_major_locator(ticker.MultipleLocator(1))
	thisplot.yaxis.set_minor_locator(ticker.MultipleLocator(1))
	#thisplot.set_yticklabels(ylbls)
	thisplot.set_title("%s\n[%.0f]" % (r.hget("team:%s" % tid, "name"), rating), y=0.7, x=0.8, fontsize=8)
	i += 1

#plt.show()
plt.savefig("rankplot_tmp3.pdf")
#print data
