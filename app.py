import argparse
import logging
from typing import Union
import os

import coloredlogs
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from clash_tools import Subscribers, Rule

app = FastAPI()
rule_names = []
rules = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/subs/{sub_file}/{rule_file}", response_class=PlainTextResponse)
def read_item(sub_file: str, rule_file: str, q: Union[str, None] = None):

    sub_file = os.path.join("configs/", sub_file + ".yaml")
    rule_file = os.path.join("configs/", rule_file + ".yaml")

    subscribers = Subscribers(sub_file)
    
    rule= Rule(rule_file, subscribers)


    return rule.generate_config()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="clash subsriber server")

    argparser.add_argument("--port", type=int, default=8000)
    argparser.add_argument("--host", type=str, default="0.0.0.0")
    argparser.add_argument("-v", "--verbose", action="store_true")

    args = argparser.parse_args()

    coloredlogs.install()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    

    uvicorn.run(
        "app:app", host=args.host, port=args.port, log_level="debug", reload=True
    )
