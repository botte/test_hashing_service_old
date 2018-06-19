# test_hash_service

Python2 / PyTest tests for 'ACME Password Hash Service.'

## Getting Started
```
Service MUST be running on PORT=8088.
It is highly recommended installing the test suite into a Python virtual environment.
```

## NOTE
```
Test suite was ONLY run and tested on Ubuntu 6.04.1.
Tests only verified using python2.
NOTE: Tests will NOT run correctly with python3.
```

### Prerequisites
```
4G RAM

Python2.7.x
pip (setup.py will install package dependencies)

NOTE: Tests will NOT run correctly with python3.
```

### Installing and running
```
Launch the service on PORT=8088.
In base project directory, run
1. pip install .
2. python2 run_tests.py
```

### Test results output 
Test results are written only to the console.
Results should appear as...
```
python run_tests.py 
======================================= test session starts ========================================
platform linux2 -- Python 2.7.12, pytest-3.6.1, py-1.5.3, pluggy-0.6.0
rootdir: /home/user/test_hash_service, inifile:
collected 7 items                                                                                  

test/tests/test_1_post_get.py ....F.F

============================================= FAILURES =============================================
/home/user/test_hash_service/test/tests/test_1_post_get.py:138: AssertionError: POST password w/ punctuation; password= /=\
/home/user/test_hash_service/test/tests/test_1_post_get.py:168: AssertionError: GET/stats should not accept data.
=============================== 2 failed, 5 passed in 120.46 seconds ===============================
======================================= test session starts ========================================
platform linux2 -- Python 2.7.12, pytest-3.6.1, py-1.5.3, pluggy-0.6.0
rootdir: /home/user/test_hash_service, inifile:
collected 1 item                                                                                   

test/tests/test_2_shutdown.py 
...


For greater verbosity, edit 'run_tests.py' by swapping the commented commands.
NOTE: 
PyTest prints results on a per module/per test function basis.
Test module 'test_2_shutdown.py' only contains one test function and a failing test result only counts as one failure.
However, if the test fails, the test function reports all failures at the bottom of the output.
```

## About the tests

### Errors found during testing

These five errors are repeatable running the automated test suite.

        POST to /hash should accept a password
            Error: POST password w/ punctuation; password= ,@\

        GET to /stats should accept no data
            Error: GET/stats should not accept data.

        GET to /hash should accept a job identifier
            Error: GET id status text, Service Unavilable.

        GET to hash should return base64 encoded password hash for corresponding POST request
	    Error: GET id encoding error.

        No additional password requests should be allowed when shutdown pending
	    Error: No additional password requests when shutdown pending.
 

### What was not tested 
```
1. GET stats API call - average time of a hash request in milliseconds.
   Exclusion based on cost/benefit analysis.
2. Uncertain if this test requirement is being fulfilled 
       'server processes multiple connections simultaneously'
```


### The automated tests
```
Python pytest is used for convenience of the assert statement and for the 'fixtures.' 
Each tested 'testable requirement' is listed in the corresponding test code function. 
Test modules are launched, in order, by running 'python2 run_tests.py.'
The two pytest test modules are
1. test_1_post_get.py (no shutdown API call)
- test_post_hash_general
- test_post_hash_timing - test with multiple connections
- test_post_hash_sha512
- test_big_password
- test_bad_passwords
- test_stats
- test_stats_with_data

2. test_2_shutdown.py
- test_shutdown - verify graceful server shutdown

Observations
1. I did not convince myself I was simulating multiple simultaneous connections in the test automation.
   The concern is missing a failing requirement.
2. The automated testing is a first-pass best effort.
```


### Tests run manually 
```
The purpose of initially testing manually is at least four-fold
1. Become familiar with the service and with calling the service API.
2. Become familiar with the testable requirements and what testing them entails.
3. Look for 'low hanging fruit' test ideas.
4. Look for tests that appear to pass and that would be difficult to include in an automated test suite.
   These tests can be coded at a later date.
   The primary concerns found for this project include
    1. The requirement 'server processes multiple connections simultaneously.'
    2. Avoiding saving test state between test invocations.

Observations
1. Once the 'shutdown' API is called, all server state is lost. 
2. For initial test scripting, I wanted to avoid server restarts.
3. Test state is not maintained between pytest invocations.

Conclusions
1. I was not certain of the meaning of the test requirement phrase 'multiple connections simultaneously.'
   I believe I simulated multiple simultaneous connections during manual tests (see below).
   During this part of manual testing I did not observe any server issues.
   However, collecting and comparing server state when manually running test scripts is untenable.
   The concern is missing a failing requirement.
2. End all testing with one (only one) shutdown API call. 
```
```
Manual testing using curl commands
1. Run each command on an unpopulated service.
2. Run each command on a populated service.
3. 'ctrl c' service, restart, and repeat steps 1 and 2.

Using bash scripts containing curl commands containing multiple API calls
1.  Run load tests on POST/hash various passwords and verify with curl commands.
2.  Run load tests on GET/ id and verify results.
2.  Run load tests on GET/stats and verify results.

Using a bash script containing the previously created bash scripts
- Test scripts will run with different PPID - multiple simultaneous connections
- The purpose is to simulate a multi-client environment.
- Test scripts DO NOT contain the shutdown call.
1. Run various script configurations, observer the server, test output, and query the server.

Using a bash script containing the previously created bash scripts
- Test scripts will run with different PPID - multiple simultaneous connections
- The purpose is to simulate a multi-client environment.
- Test scripts DO contain the shutdown call.
1. Run various script configurations, observer the server, test output, and query the server.
```
