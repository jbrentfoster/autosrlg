Script for automating SRLG assignment through EPNM RESTconf API.

Setup Instructions

* Create a Python 3.x virtual environment.

Example,

`$ python3.6 -m venv py3-venv`

* Activate the virtual environment.

Example,

```
$ source py3-venv/bin/activate
(py3-venv)$`
```

* Install requests & tornado 

Example,
```
(py3-venv)$ pip install requests
(py3-venv)$ pip install tornado
```


To execute the script:

    python server.py --port [port number]

Example,

    (py3-venv) python server.py --port 8003
    
Navigate web browser to the IP:Port number

Example,

http://127.0.0.1:8003/