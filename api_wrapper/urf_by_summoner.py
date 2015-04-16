from api_wrapper import ApiWrapper
from API_KEY import API_KEY
from collections import deque
import pickle
import os
import sqlite3
import FILES

MAX_GAMES_TO_PROCESS = 1000000
# Summoner_list defaults with the following summ_id's
# obesechicken Atolight DeanieMan Gizekaze CZealot
DATS_FILES_AND_DEFAULTS = (('summoners', FILES.SUMMONER_FILE, deque([25409247, 19167004, 28219700, 25401107, 19174197])),
                           ('processed_games', FILES.GAME_FILE, set()),
                           ('processed_summs', FILES.PROSCESSED_SUMM_FILE, set()))


class UrfSummonerCrawler(object):

    def __init__(self):
        self.api = ApiWrapper()
        self.processed_games = set()
        self.conn = sqlite3.connect(FILES.SQLLITE_FILE)
        self._setup_db()

        self._set_persistance()

    def _setup_db(self):
        self.conn.cursor().execute('''CREATE TABLE IF NOT EXISTS test_data(
                                        summ_id integer,
                                        champ_id integer,
                                        result integer)
                                   ''')

    def _set_persistance(self):
        """ Sets summoner_list, processed_games_list and processed_summoners_list
        """
        for dat, fname, default in DATS_FILES_AND_DEFAULTS:
            if os.path.exists(fname):
                with open(fname, 'rb') as f:
                    setattr(self, dat, pickle.load(f))
            else:
                setattr(self, dat, default)

    def _save_persistance(self):
        for dat, fname, _ in DATS_FILES_AND_DEFAULTS:
            with open(fname, 'wb') as f:
                pickle.dump(getattr(self, dat), f)

    def _insert_row(self, summoner, summ_champion, win):
        self.cur.execute(''' INSERT INTO test_data
                        (summ_id, champ_id, result)
                        VALUES (?, ?, ?)
                    ''', (summoner, summ_champion, win))

    def _extract_summ(self, game):
        summ_team = game['teamId']
        win = game['stats']['win']
        summ_champion = game['championId']
        return (summ_team, win, summ_champion)

    def _extract_fellow(self, fellow):
        fsumm = fellow['summonerId']
        fchamp = fellow['championId']
        fteam = fellow['teamId']
        return (fsumm, fchamp, fteam)

    def crawl(self):
        self.cur = self.conn.cursor()
        print('''
                 Beginning crawl...
                 From previous session (if one existed):
                 Processed games: {}
                 Prcesssed Summoners: {}
                 Summoners left to process: {} (This will grow as execution continues)

              '''.format(len(self.processed_games),
                         len(self.processed_summs),
                         len(self.summoners)))

        while self.summoners and len(self.processed_games) <= MAX_GAMES_TO_PROCESS:
            summoner = self.summoners.popleft()
            if summoner in self.processed_summs:
                # skip if we've looked at summ's recent games already
                continue

            url = self.api.game_by_summoner(summoner)

            recent_games = self.api.api_call(url)['games']
            for game in recent_games:
                game_id = game['gameId']
                # only parse URF games we haven't seen before
                if game['subType'] == 'URF' and game_id not in self.processed_games:
                    summ_team, win, summ_champion = self._extract_summ(game)
                    self._insert_row(summoner, summ_champion, win)

                    # Go through each fellow player
                    # and calculate if they won or lost based on if they
                    # are on the current summoners team.
                    for fellow in game['fellowPlayers']:
                        fsumm, fchamp, fteam = self._extract_fellow(fellow)
                        # Winners are fellows on the summoners team
                        if fteam == summ_team:
                            fwin = win
                        else:
                            fwin = not win

                        self._insert_row(fsumm, fchamp, fwin)
                        # Add the summoner to the list of summoners to process later
                        # because they've probably played more urf games
                        if summoner not in self.processed_summs:
                            self.summoners.append(fsumm)

                    self.processed_games.add(game_id)

                    if len(self.processed_games) % 100 == 0:
                        # Every 100 games, write info to db
                        print('Completed ', str(len(self.processed_games)), 'games')
                        self.conn.commit()
                        self._save_persistance()

            self.processed_summs.add(summoner)

        self.conn.commit()
        self._save_persistance()

    def make_champ_list(self):
        data = self.api.issue_api_call('https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?dataById=true&champData=info&api_key=%s' % (API_KEY, ))
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS champ_data(
                                champ_id integer,
                                name text)
                           ''')
        cur.execute('DELETE FROM champ_data')

        for key, value in data["data"].items():
            cur.execute(''' INSERT INTO champ_data
                            (champ_id, name)
                            VALUES (?, ?)
                        ''', (int(value["id"]), value["name"]))
        self.conn.commit()

if __name__ == '__main__':
    ufc = UrfSummonerCrawler()
    # ufc.make_champ_list()
    ufc.crawl()
