# A Very Basic Rest API for Remote Executing a Command
    This simple program implements a basic API to execute a command on a remote server.

    It uses a get command with parameters, e.g.,

        - 1) EXECUTE   http://127.0.0.1:5000/execute?cmd="ls"&options="-lhstra1R"&path="./TEST"

        - 2) SHUTDOWN  http://127.0.0.1:5000/shutdown

    Valid options are:

        -l -h -s -t -r -R -a -1


# PARAMETERS
    - 1) INPUT: (cmd executed, options, path)
    ```
        "cmd": "ls",
        "options": "-lsh",
        "path": "./TEST"
    ```

    - 2) OUTPUT: (cmd executed, request_id, output)
    ```
        "cmd": "ls  ",
        "rid": "2196",
        "out": "Try later, too many requests from ip within recent window"
    ```



# LIMITATIONS
    It imposes a number of most basic (from the hip) security checks to the command against attacks. 
    It throtles request to a maximum of nmax (100) jobs within a window of tmax (1) seconds.
    It remembers the current pending jobs.
    It limits the number of directories to list to one. 
    It executes every request on a separate thread.
    It executes every command in a restricted shell.
    It imposes check on valid options passed.
    Testing is currently functionally based, by hand --- waiting to be migrated to unittest


# DESCRIPTION
DESCRIPTION
     For each operand that names a file of a type other than directory, ls displays its name as
     well as any requested, associated information.  For each operand that names a file of type
     directory, ls displays the names of files contained within that directory, as well as any
     requested, associated information.

     If no operands are given, the contents of the current directory are displayed.  If more than
     one operand is given, non-directory operands are displayed first; directory and non-directory
     operands are sorted separately and in lexicographical order.

  
# GETTING STARTED
  - 1) Install requirements
  pip3 install flask
  pip3 install flask-requests
  pip3 install flask-restful
  pip3 install asyncio

  - 2) Run the server
  python3 api.py

  - 3) Run a test client
       - a) shell
            ./curl_test.sh

       - b) python
            python3 client.py



# ARCHITECTURAL NOTES
    1) server entry point providing client api : execute and shutdown
       execute commands dispatched into asyncio coroutine
       every 10 of such request is injected an anomalous large delay  
    2) command validator object analyzes input command for exploits and correctness 
    3) cache/history object keeps track of request load per window time, at this time, on ip basis
    4) pending_request object keeps track of currently being processed objects
    5) shutdown object triggers event signal to disable serving new requests 

# CONTACT
    nelsonr@umich.edu
