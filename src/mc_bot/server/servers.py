from fabric import Connection

import os
import csv
import logging

FILE_NAME = "servers.txt"
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w") as f:
        pass


def get_servers():
    server_map = {}
    print("am i getting caleld?")
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", newline='') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                print(f"{row}")
                if len(row) == 2:
                    server_map[row[0]] = row[1]
    print(f"{server_map}")
    return server_map

def save_server(name: str, command: str, logger: logging.Logger):
    current_servers = get_servers()
    
    if any(s.lower() == name.lower() for s in current_servers.keys()):
        return False

    with open(FILE_NAME, "a", newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow([name, command])

        logger.info(f"created server {name} command is {command}")
    return True

def run_server(name: str, logger: logging.Logger, ip, user, key_path):
    current_servers = get_servers()
    if name not in current_servers:
        return False

    cmd = current_servers[name]
    connect_params = {
        "key_filename": os.path.expanduser(key_path),
    }
    with Connection(host=ip, user=user, connect_kwargs=connect_params) as c:
        logger.info(f"Connected using key: {key_path}")
        logger.info(f"Running command: {cmd}")
        
        c.run(cmd)



