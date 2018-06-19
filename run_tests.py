""" Main test entry point for running all /tests/'tests.py' """
import pytest
import time


def run_1_post_get():
    """ """
    pytest.main(['-s', '--tb=line', 'test/tests/test_1_post_get.py'])
    #pytest.main(['-s', '-v', 'test/tests/test_1_post_get.py'])


def run_2_shutdown():
    pytest.main(['-s', '--tb=line', 'test/tests/test_2_shutdown.py'])
    #pytest.main(['-s', '-v', 'test/tests/test_2_shutdown.py'])


if __name__ == '__main__':
    run_1_post_get()
    time.sleep(60)
    run_2_shutdown()
