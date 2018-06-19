""" Verify post /hash 'password', get 'job_id.'

    When launched, the application should wait for http connections.
        - It should answer on PORT specified in the PORT environment variable.
        - It should support endpoints
            - POST to /hash should accept a password
            - POST to /hash should return a job identifier immediately
            - The hashing algorithm should be SHA512

            - GET to /hash should accept a job identifier
            - GET to hash should return the base64 encoded password hash for
              the corresponding POST request
            - GET to /stats should
                - Accept no data
                - Return a JSON data structure
                - Since the server statrted return
                    - total hash requests
                    - average time of a hash request in milliseconds.
"""

from multiprocessing import Process, Array, Value
import requests
import ctypes, json, time
from test.lib import lib


def test_post_hash_general(post, calls):
        """ When launched, the application should
                - wait for http connections and
                - answer on the PORT specified in the PORT environment variable.
            POST to /hash should accept a password.
            POST to /hash should return a job identifier immediately.
        """

        response = post('/hash', 'password')
        calls()
        assert response.status_code == requests.codes.ok, \
                'POST failed {}'.format(response.status_code)
        assert response.text != '', 'POST did not return job id'



def test_post_hash_timing(post, get, calls):
    """ POST to /hash should wait 5 seconds and compute the password hash. """

    def stack_error(errors, error):
        for i in range(len(errors)):
            if  not errors[i]:
                errors[i] = error
                break


    def client_post(pid, errors):
        try:
            post_response = post('/hash', 'password')
            pid.value = int(post_response.text)
        except Exception as e:
            stack_error(errors, b'Excpetion encountered when put /hash "password"')


    def client_get(pid, errors):
        for i in range(5):
            try:
                get_response = get('/hash/' + str(pid))
                if get_response.status_code == requests.codes.ok:
                    stack_error(errors, \
                            b'Computing password hash took less than 5 seconds.')
            except Exception as e:
                stack_error(errors, b'Exception encountered when get /hash/id.')
            time.sleep(1)


    errors = Array(ctypes.c_char_p, 2)
    for i in range(len(errors)):
        errors[i] = None

    pid = Value('i', 666)

    post_client = Process(target = client_post, args=(pid, errors))
    get_client = Process(target = client_get, args=(pid, errors))

    post_client.start()
    get_client.start()
    get_client.join()

    calls()

    for i in range(len(errors)):
        if errors[i]:
            assert False, 'Error ' + errors[i]



def test_post_hash_sha512(post, get, calls, random_passwords, generate_sha512):
    """ The hashing algorithm should be SHA512.
        GET to /hash should accept a job identifier.
        GET to hash should return the base64 encoded password hash for the
        corresponding POST request.
    """

    for password in random_passwords:
        response = post('/hash', password)
        calls()
        assert response.status_code == requests.codes.ok, 'POST failed'
        assert response.text, 'POST response.text was empty.'


        """ hash should return base64 encoded password. """
        response2 = get('/hash/' + str(response.text))
        res_data = response2.text
        assert lib.is_base64(response2.text), 'Password was not base64.'
        assert response2.status_code == requests.codes.ok, \
                'Service did not return hash.'


        """ The hashing algorithm should be SHA512. """
        gen_data = generate_sha512(password)
        assert gen_data == res_data, 'Password was  not sha512'



def test_big_password(post, calls, big_password):
    """ POST to /hash should accept a password. """
    for password in big_password:
        response = post('/hash', password)
        calls()
        assert response.status_code == requests.codes.ok, \
                'POST big password; password= ' + password



def test_bad_passwords(post, calls, random_passwords_punc):
    """ POST to /hash should accept a password. """

    for password in random_passwords_punc:
        response = post('/hash', password)
        calls()
        assert response.status_code == requests.codes.ok, \
                'POST password w/ punctuation; password= ' + password



def test_stats(get_with_data, get_calls, get_no_header):
    """ GET to /stats should...
            - Return a JSON data structure
                - since the server statrted return
                    - total hash requests
                    - average time of a hash request in milliseconds.
    """
    # {"TotalRequests":5,"AverageTime":141412}
    response = get_no_header('/stats')
    assert response.status_code == requests.codes.ok, 'GET/stats failed.'

    as_json = json.loads(response.text)
    assert as_json['TotalRequests'], 'Invalid json format or TotalRequests not set.'
    assert as_json['AverageTime'], 'Invalid json format or TotalRequests not set.'

    cnt_recorded = get_calls()
    cnt_reported = as_json['TotalRequests']
    assert str(cnt_recorded) == str(cnt_reported), \
            'Recorded requests: {}, reported requests: {}'.format(cnt_recorded, cnt_reported)



def test_stats_with_data(get_with_data, get_no_header):
    """ GET to /stats should accept no data. """
    response = get_with_data('/stats')
    assert response.status_code != requests.codes.ok, 'GET/stats should not accept data.'
