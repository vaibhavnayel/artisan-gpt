from typing import Dict, List
from pprint import pformat
import logging

from fastapi import FastAPI
from model import Model

model = Model()
app = FastAPI()

@app.post("/chat")
def chat(message_thread: List[Dict[str, str]]):
    logging.debug(f"{pformat(message_thread)}")
    return model.chat(message_thread)
