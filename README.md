# Purpose
This repository was made to hold a LAN multiplayer game

# Demonstration
https://www.reddit.com/r/pygame/comments/131t90l/presented_this_in_my_distributed_systems_class/

# Dependencies
Look at requirements.txt for dependencies to download before running. The server itself only uses 
base python3 libraries, but the client requires extra packages.

```
pip3 install -r requirements.txt
```

# Running
To run the system, first start the server:

```
python3 server.py
```

This should then tell you the IP and port that the system is running on.
Make sure the client is on the same wifi and now try:

```
python3 client.py
```

This will open (if successfully installed) a pygame window.
From here, you need to correctly input the IP, port, and 
whatever username you want. 

NOTE: USE THE ARROW KEYS TO CHANGE WHAT FORM YOU'RE TYPING TO
