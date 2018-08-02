Script for automating SRLG assignment through EPNM RESTconf API.

Setup Instructions

1) Create a Python 2.7 virtual environment.

2) Activate the virtual environment.

3) Install requests

    pip install requests



To execute the script:

    python main.py <temp directory> <EPNM IP addr> <EPNM user> <EPNM pass>

Example,

    (AutoSRLG) C:\Users\brfoster\PycharmProjects\AutoSRLG>python main.py "C:\Users\brfoster\Temp_SRLG" "10.135.7.223" "root" "Epnm1234"