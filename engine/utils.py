import json
import sys

EOF = "<EOF>"

def log(*values):
    sys.stdin.flush()
    data = {}
    data["log"] = " ".join([str(val) for val in values])
    print(json.dumps(data) + EOF, flush=True)

def send(json_msg):
    print(json.dumps(json_msg) + EOF, flush=True)