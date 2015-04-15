from api_wrapper import ApiWrapper
from collections import deque
import pickle
import os
import sqlite3

MAX_GAMES_TO_PROCESS = 100005
SUMMONER_FILE = '/home/craig/windrive/Temp/summoners.pickle'
GAME_FILE = '/home/craig/windrive/Temp/processed_games.pickle'
PROSCESSED_SUMM_FILE = '/home/craig/windrive/Temp/processed_summ.pickle'
# Summoner_list defaults with the following summ_id's
# obesechicken Atolight DeanieMan Gizekaze CZealot
DATS_FILES_AND_DEFAULTS = (('summoners', SUMMONER_FILE, deque([25409247, 19167004, 28219700, 25401107, 19174197])),
                           ('processed_games', GAME_FILE, set()),
                           ('processed_summs', PROSCESSED_SUMM_FILE, set()))


class UrfSummonerCrawler(object):

    def __init__(self):
        self.api = ApiWrapper()
        self.processed_games = set()
        self.conn = sqlite3.connect('/home/craig/windrive/Temp/testdb.db')
        self._setup_db()

        self.__set_persistance()

    def _setup_db(self):
        self.conn.cursor().execute('''CREATE TABLE IF NOT EXISTS test_data(
                                        summ_id integer,
                                        champ_id integer,
                                        result integer)
                                   ''')

    def __set_persistance(self):
        """ Sets summoner_list, processed_games_list and processed_summoners_list
        """
        for dat, fname, d in DATS_FILES_AND_DEFAULTS:
            if os.path.exists(fname):
                with open(fname, 'rb') as f:
                    setattr(self, dat, pickle.load(f))
            else:
                setattr(self, dat, d)

    def save_persistance(self):
        for dat, fname, _ in DATS_FILES_AND_DEFAULTS:
            with open(fname, 'wb') as f:
                pickle.dump(getattr(self, dat), f)

    def crawl(self):
        summoners = self.summoners
        cur = self.conn.cursor()
        while len(self.processed_games) <= MAX_GAMES_TO_PROCESS:
            summoner = summoners.popleft()
            if summoner in self.processed_summs:
                continue
            url = self.api.game_by_summoner(summoner)
            recent_games = self.api.api_call(url)['games']
            for game in recent_games:
                game_id = game['gameId']
                # only parse URF games we haven't seen before
                if game['subType'] == 'URF' and game_id not in self.processed_games:
                    self.processed_games.add(game_id)
                    if len(self.processed_games) % 100 == 0:
                        print('Comepleted ', str(len(self.processed_games)), 'games')
                        self.conn.commit()
                    summ_team = game['teamId']
                    win = game['stats']['win']
                    summ_champion = game['championId']

                    cur.execute(''' INSERT INTO test_data
                                            (summ_id, champ_id, result)
                                            VALUES (?, ?, ?)
                                ''', (summoner, summ_champion, win))

                    # Go through each fellow player
                    # and calculate if they won or lost based on if they
                    # are on the current summoners team.
                    for fellow in game['fellowPlayers']:
                        fsumm = fellow['summonerId']
                        fchamp = fellow['championId']
                        fteam = fellow['teamId']
                        if fteam == summ_team:
                            fwin = win
                        else:
                            fwin = not win

                        cur.execute(''' INSERT INTO test_data
                                            (summ_id, champ_id, result)
                                            VALUES (?, ?, ?)
                                    ''', (fsumm, fchamp, fwin))

                        # Add the summoner to the list of summoners to process
                        # because they've probably played more urf games
                        summoners.append(fsumm)

            self.conn.commit()
            self.save_persistance()

if __name__ == '__main__':
    ufc = UrfSummonerCrawler()
    try:
        ufc.crawl()
    except:
        ufc.conn.commit()
        ufc.save_persistance()
