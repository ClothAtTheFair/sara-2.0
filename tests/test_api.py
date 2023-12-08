import pytest
import random
from ..sara import SARA
#Fix this
from api.sara_api import status

def __setup():
    #To run the tests, we need an instance of sara (minimal), running 
    sara = SARA()

#Test to see if the status of sara (working, error, exited, etc. can be pulled from the api)
def test_get_status():
    #We assume Sara is running
    expected_response = 200
    assert status() == expected_response

def __run_tests():
    test_get_status()

if __name__ == "__main__":
    __setup()
    __run_tests()