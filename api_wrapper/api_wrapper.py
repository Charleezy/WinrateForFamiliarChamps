import urllib.request
import urllib.error
from urllib.error import HTTPError
from API_KEY import API_KEY
import time
import logging
import json
import threading
import queue


SHORT_TIME_LIMIT = 10.5
SHORT_MAX_REQUESTS = 10

LONG_TIME_LIMIT = 605
LONG_MAX_REQUESTS = 500

MAX_REQUEST_HTTP_CODE = 429

HIGHEST_PRIORITY = 0

NUM_THREADS = 10


class MaxReqsException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ApiWrapper(object):

    def __init__(self):
        self.lock = threading.Lock()

        self.request_queue = queue.PriorityQueue()
        self.result_queue = queue.Queue()

        # Stores times of requests made with the last SHORT_TIME_LIMIT seconds
        self.short_limit = [time.time(), 0]

        # Similar to above except for LONG_TIME_LIMIT
        self.long_limit = [time.time(), 0]

        for i in range(NUM_THREADS):
            t = threading.Thread(target=self.worker_thread)
            t.daemon = True
            t.start()

    def _constraint_check(self):
        """ Does all of its checks/updates with the class wide lock...so only
            one thread will be accessing the API at a time. There is no persistance
            between runs so this won't account for runs in the last
            10 minutes that were stopped.
        """
        with self.lock:
            now = time.time()
            if now - self.long_limit[0] > LONG_TIME_LIMIT:
                # reset the long time limit and counter if we've crossed it
                self.long_limit = [now, 0]
            elif self.long_limit[1] == LONG_MAX_REQUESTS:
                timeleft = LONG_TIME_LIMIT - (now - self.long_limit[0])
                logging.info('LONG LIMIT REACHED, wait {0} seconds'.format(timeleft, ))
                return timeleft

            # This is pretty much repeating what the above checks do except for
            # the short time limit, should probably refactor at some point.
            if now - self.short_limit[0] > SHORT_TIME_LIMIT:
                # reset the short time limit and counter
                self.short_limit = [now, 0]
            elif self.short_limit[1] == SHORT_MAX_REQUESTS:
                timeleft = SHORT_TIME_LIMIT - (now - self.short_limit[0])
                logging.info('SHORT LIMIT REACHED, wait {0} seconds'.format(timeleft, ))
                return timeleft

            self.long_limit[1] += 1
            self.short_limit[1] += 1
            return 0

    def worker_thread(self):
        """ Grabs a request off the queue, sleeps if its hitting the rate
            limit and returns. If the RIOT API returns a 429 code
            (too many request within the alotted time..although this should rarely
            happen since the call to _constraint_check should handle the waiting)
            the thread will just put the request back on the queue to be serviced by
            another thread.
        """
        while True:
            # throwaway the first argument...its just the priority
            _, url, callback = self.request_queue.get()
            while True:
                timeleft = self._constraint_check()
                if timeleft > 0:
                    time.sleep(timeleft)
                else:
                    break
            try:
                data = self.issue_api_call(url)
            except MaxReqsException:
                # If we've gotten this exception then our rate limiting hasn't
                # worked for some reason. Put the request back on the queue
                # with a high priority to get serviced
                self.request_queue.put((HIGHEST_PRIORITY, url, callback))
            else:
                # Sucess case, put it on the result queue
                # Sleep so we aren't too agressive in case we are breaking
                # the longer time constraint because of a previous run.
                time.sleep(10)
                self.result_queue.put((data, callback))
            finally:
                self.request_queue.task_done()

    @staticmethod
    def issue_api_call(url):
        try:
            f = urllib.request.urlopen(url)
        except HTTPError as e:
            if e.code == 429:
                logging.warning('Exceeded threshold, will retry')
                raise MaxReqsException(e.code)
            raise
        data = json.loads(f.read().decode('utf-8'))
        return data


if __name__ == '__main__':
    for _ in range(4):
        print(ApiWrapper.issue_api_call('https://na.api.pvp.net/api/lol/na/v1.2/champion/102?api_key={0}'.format(API_KEY, )))
