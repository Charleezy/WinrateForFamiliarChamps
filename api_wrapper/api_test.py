from api_wrapper import ApiWrapper
from api_wrapper import API_KEY
import threading


NUM_THREADS = 10


class ApiCaller(object):

    """
    Tests the rate limiting features of the api_wrapper.
    Puts requests on the request queue and then pops results off the
    result queue from the api wrapper. The callback function it uses
    is print so if it works properly the results will simply be printed
    to the consolse
    """

    def __init__(self):
        self.api = ApiWrapper()
        for i in range(NUM_THREADS):
            t = threading.Thread(target=self.worker_thread)
            t.daemon = True
            t.start()

    def worker_thread(self):
        while True:
            data, callback = self.api.result_queue.get()
            callback(data)
            self.api.result_queue.task_done()

if __name__ == '__main__':
    ac = ApiCaller()
    # 22 requests
    print('===========Callback Test==========')
    for _ in range(22):
        ac.api.api_call(url='https://na.api.pvp.net/api/lol/na/v1.2/champion/102?api_key={0}'.format(API_KEY, ), priority=5, callback=print)

    print('===========Blocking Test==========')
    for _ in range(15):
        print(ac.api.api_call(url='https://na.api.pvp.net/api/lol/na/v1.2/champion/102?api_key={0}'.format(API_KEY, )))
    ac.api.request_queue.join()
    ac.api.result_queue.join()
