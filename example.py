import LoLpy
API_KEY = "8c5f8ce1-be1d-4b4f-9782-1e2e77bcbcb8"#Charlie's API key


def main():
	print "Let's get started!"
	lolpy = LoLpy.LoLpy(API_KEY)
	# account = lolpy.get_summoner_by_name('Dyrus')['Dyrus'.lower()]
	# league = lolpy.get_league_by_id(account['id'])
	# ranked = lolpy.get_stats_ranked('Dyrus')
	# print ranked
	matches = lolpy.get_api_challenge(1428126000)
	print(matches)
	import pymysql
	conn = pymysql.connect(host='127.0.0.1', user='root', passwd=None)
	cur = conn.cursor()
	for match in matches:
		cur.execute("INSERT INTO `urf`.`urf_matches` (`id`, `matchid`) VALUES (NULL, mach);")
	cur.close()
	conn.close()
	#Time
	import calendar
	import time as t
	import datetime as dt
	cur_time_formed = t.strftime("%Y-%m-%d %H:%M:%S", t.gmtime())
	#Epoch time
	cur_epoch_time = calendar.timegm(t.strptime(cur_time_formed, '%Y-%m-%d %H:%M:%S'))
	#12 am this day. Do not run cron anywhere between 11:40p and 12:01a whatever time zone you're working in. Unless changed, we're using UTC
	today_midn = Decimal(cur_time) % 86400 - cur_time
	#Tbh, I could just manually populate the table using sleep for the api limit issue, and then run the script on the hour. 
	#It'll just mean you can never test the script because testing the script will create dupes.
	#Or run the script for all data since Urf mode was released, using latest database timestamp if the database table is not empty
	#and use sleeps to bypass api limit issue
	


if __name__ == "__main__":
	main()
