from queue import Queue
from TestClient import Client
from string import ascii_letters, digits
from random import *
import communication
from threading import Thread


def run_test(tests: Queue):
    while tests.empty() is False:
        client, request = tests.get()
        c_thread = Thread(target=client.test, args=(request,))
        c_thread.start()


if __name__ == '__main__':
    test_clients = Queue()
    for i in range(10):
        user_name = ''.join(sample(ascii_letters, randint(5, 15)))
        password = ''.join(sample(ascii_letters + digits, randint(5, 15)))
        action = communication.ACTIONS[choice(range(0, 2))]
        req = {
            'user': {'user_name': user_name, 'pass': password},
            'action': action
        }

        c = Client('test_client_' + str(i+1))
        test_clients.put((c, req))

    c1 = Client('test_client_11')
    c1_req = {
        'user': {"user_name": "teste_arquivos", "pass": "testpasss"},
        'action': communication.ACTIONS[0]
    }

    test_clients.put((c1, c1_req))
    run_test(test_clients)