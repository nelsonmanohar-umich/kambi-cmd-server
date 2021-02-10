import requests
import time
import unittest
import argparse



# documentation of the valid options accepted by the server for the ls command
VALID_OPTIONS = "-lst1hrafR"


# api-endpoint
SERVER_URL = "127.0.0.1:5000"
URL1 = "http://%s/execute" % SERVER_URL
URL2 = "http://%s/shutdown" % SERVER_URL


# variant from code snippet from internet
def make_request(cmd="ls", path="", options="", url=URL1, header=True, debug=False):
    # defining a params dict for the parameters to be sent to the API
    if header:
        print("\n" * 3 + "-" * 32)
        print("MAKING REQUEST", url, cmd, options, path)
    try:
        PARAMS = {'cmd':cmd, "options": options, "path": path}
        # sending get request and saving the response as response object
        response = requests.get(url = url, params = PARAMS, timeout=3)
        response.raise_for_status()
        # Code here will only run if the request is successful

        # extracting data in json format
        response_data = response.json()
        if header:
            for k in response_data:
                print(k)
                for item in str.translate(response_data[k], "ascii").split("\\n"):
                    print(item)
        else:
            print("****", str(response_data))
        return response_data

    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)
    except Exception as e:
        print(e)
    return None



def shutdown_request():
    # defining a params dict for the parameters to be sent to the API
    print("\n" * 3 + "-" * 32)
    print("SHUT DOWN REQUEST")
    PARAMS = {}
    # sending get request and saving the response as response object
    try:
        response = requests.get(url = URL2, params = PARAMS, timeout=3)
        response.raise_for_status()
        # Code here will only run if the request is successful

        # extracting data in json format
        response_data = response.json()
        for k in response_data:
            print(k)
            for item in str.translate(response_data[k], "ascii").split("\\n"):
                print(item)
        return response_data

    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)
    except Exception as e:
        print(e)
    return None











class TestClientServer(unittest.TestCase):
    def test_ls01(self):
        self.assertTrue("TEST" in make_request(cmd="ls", path=".", options="-h", header=False)['out'])
        return

    def test_shutdown(self):
        self.assertTrue("OK" in shutdown_request()['out'])
        self.assertTrue(make_request(cmd="ls", path=".", options="-h", header=False) is None)
        return


def test_functional_basics():
    # default request
    make_request()

    # current directory
    make_request("ls", ".")

    # empty valid directory
    make_request("ls", "./OLD")

    # regular expression directory
    make_request("ls", "*.py", options="")
    make_request("ls", path="*.py", options="-hltras")

    # options directory
    make_request(cmd="ls", path="*.py", options="-h -l -tr -a -s")
    make_request(cmd="ls", path="*.py", options="-lh -tra -s")

    return


def test_path_basics():
    # root directory
    make_request("ls", "/")

    # upward directory
    make_request("ls", "./..")

    return


def test_bad_input_basics():
    # invalid cmd
    make_request("", "./..")
    make_request("-hshts", "ls", "./..")

    # invalid cmd
    make_request("kls", "./..")

    # invalid cmd
    make_request("lsls", ".")

    # suspicious escalation upward
    make_request("ls", "./../..")

    # suspicious string
    make_request("ls", "./../..dasdkas;lkd;aslkdakr, eval('1'),-304923d;lskadas;m42m,.m13120")

    return


# sudden load
def test_loadsurge_basics(n, stops=None, timeout=5):
    if stops is None:
        stops = list(range(100, n, 300))

    for i in range(n):
        print(i, end="--> ")
        make_request(cmd="ls", path=".", options="-h", header=False)

        # test the client respecting load balance
        if i in stops:
            time.sleep(timeout)

    return






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    print("*** rest api server url ", SERVER_URL)
    print("*** ls command options accepted", VALID_OPTIONS)
    print("*** commands accepted",  URL1, URL2)

    test_functional_basics()

    test_path_basics()

    test_bad_input_basics()

    test_loadsurge_basics(1000)

    unittest.main()

    # shutdown_request()



