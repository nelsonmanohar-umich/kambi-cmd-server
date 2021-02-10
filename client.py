import requests
import time


# valid options accepted by the server for the ls command
VALID_OPTIONS = "-lst1hrafR"


# api-endpoint
URL1 = "http://127.0.0.1:5000/execute"
URL2 = "http://127.0.0.1:5000/shutdown"


print("*** ls command options accepted", VALID_OPTIONS)
print("*** commands accepted",  URL1, URL2)





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



# default request
make_request()

# current directory
make_request("ls", ".")

# empty valid directory
make_request("ls", "./OLD")

# regular expression directory
make_request("ls", "*.py", options="-h -l -tr -a -s")
make_request("ls", path="*.py", options="-h -l -tr -a -s")
make_request(cmd="ls", path="*.py", options="-h -l -tr -a -s")
make_request(cmd="ls", path="*.py", options="-lh -tra -s")

# root directory
make_request("ls", "/")

# upward directory
make_request("ls", "./..")

# invalid cmd
make_request("kls", "./..")

# invalid cmd
make_request("lsls", ".")

# suspicious escalation upward
make_request("ls", "./../..")

# suspicious string
make_request("ls", "./../..dasdkas;lkd;aslkdakr, eval('1'),-304923d;lskadas;m42m,.m13120")

# sudden load
for i in range(1000):
    print(i, end="--> ")
    make_request(cmd="ls", path=".", options="-h", header=False)

    # test the client respecting load balance
    if i in (300, 500, 700):
        time.sleep(4)

    if i == 900:
        # shutdown request
        shutdown_request()




