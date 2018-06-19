""" Verify shutdown when server under load.

    The software should be able to process multiple connections simultaneously.
    The software should support a graceful shutdown request
        - It should allow any in-flight password hashing to complete
        - It should reject additional password requests when shutdown is pending
        - It should respond with a 200 and shutdown.

        - POST to /hash should return a job identifier immediately
            - The hashing algorithm should be SHA512

        - GET to /hash should accept a job identifier
        - GET to hash should return base64 encoded password hash for corresponding POST request

        - No additional password requests should be allowed when shutdown pending

"""

from multiprocessing import Process, Array
import requests
import pytest
import ctypes, time
from test.lib import lib


def test_shutdown(baseurl, get, post, get_no_header, generate_sha512):

    def stack_error(status, error):
        for i in range(len(status)):
            if  not status[i]:
                status[i] = error 
                break


    def test_encoding(pswd):
        """ hash should return base64 encoded password. """
        if not lib.is_base64(pswd):
            return 'Response to get /id not base64 encoded.'

        """ The hashing algorithm should be SHA512. """
        gen_data = generate_sha512('password')
        if not gen_data == pswd:
            return 'Response to get /id not sha512.'


    def test_post1(status):
        try:
            response = requests.post(baseurl + '/hash', data = '{"password":"password"}')

            if response.status_code != requests.codes.ok:
                stack_error(status, b'POST hash status code is not 200.')

            if response.status_code == requests.codes.ok:
                response2 = requests.get(baseurl + '/hash/' + str(response.text))

                if response2.status_code != requests.codes.ok:
                    stack_error(status, b'GET id status text, Service Unavilable.')
                    if test_encoding(response2.text):
                        stack_error(status, b'GET id encoding error.')

        except Exception as e:
            ex_type = e.__class__.__name__
            if ex_type != 'ConnectionError':
                stack_error(status, b'Exception when post to hash password.')


    def test_post2(status):
        try:
            response = requests.post(baseurl + '/hash', data = '{"password":"password"}')

            if response.status_code != requests.codes.ok:
                stack_error(status, b'POST hash status code is not 200.')

            if response.status_code == requests.codes.ok:
                response2 = requests.get(baseurl + '/hash/' + str(response.text))

                if response2.status_code != requests.codes.ok:
                    stack_error(status, b'GET id status text, Service Unavilable.')
                    if test_encoding(response2.text):
                        stack_error(status, b'GET id encoding error.')

        except Exception as e:
            ex_type = e.__class__.__name__
            if ex_type != 'ConnectionError':
                stack_error(status, b'Exception when post to hash password.')
             

    def test_shutdown(status):
        try:
            response = requests.post(baseurl + '/hash', data = 'shutdown')

            if response.status_code != requests.codes.ok:
                stack_error(status, b'Response to shutdown status_code not 200.')

            if response.status_code == requests.codes.ok:
                # Now know shutdown request was received by server.
                try:
                    response2 = requests.post(baseurl + '/hash', data = '{"password":"password"}')
                    if response2.status_code == requests.codes.ok:
                        stack_error(status, b'No additional password requests when shutdown pending.')
                except Exception as e:
                    stack_error(status, b'When shutdown, exception when post to hash password.')

        except Exception as e:
            stack_error(status, b'Response to shutdown threw exception, not graceful exit.')



    array = Array(ctypes.c_char_p, 16)
    for i in range(len(array)):
        array[i] = None


    for i in range(2000):
        post1 = Process(target = test_post1, args=[array])
        post1.start()
        post2 = Process(target = test_post2, args=[array])
        post2.start()
        if i == 1999:
            post2.join()
        if i == 500:
            get = Process(target = test_shutdown, args=[array])
            get.start()

     
    print('\n\tError: ' + '\n\tError: '.join(x for x in array if x))
    assert False, 'See directly above for errors.'
