from api_wrapper import ApiWrapper
from collections import deque

MAX_GAMES_TO_PROCESS = 5


class UrfSummonerCrawler(object):

    def __init__(self):
        self.api = ApiWrapper()
        self.processed_games = set()

    def crawl(self, seed):
        summoners = deque()
        summoners.append(seed)
        while len(self.processed_games) < MAX_GAMES_TO_PROCESS:
            summoner = summoners.popleft()
            url = self.api.game_by_summoner(summoner)
            recent_games = self.api.api_call(url)['games']
            for game in recent_games:
                game_id = game['gameId']
                # only parse URF games we haven't seen before
                if game['subType'] == 'URF' and game_id not in self.processed_games:
                    self.processed_games.add(game_id)
                    summ_team = game['teamId']
                    win = game['stats']['win']
                    summ_champion = game['championId']
                    print('Summoner {0} on champion {1}. Win: {2}'
                          .format(summoner, summ_champion, win))

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
                        print('Summoner {0} on champion {1}. Win: {2}'
                              .format(fsumm, fchamp, fwin))

                        # Add the summoner to the list of summoners to process
                        # because they've probably played more urf games
                        summoners.append(fsumm)

if __name__ == '__main__':
    UrfSummonerCrawler().crawl(seed=25409247)
