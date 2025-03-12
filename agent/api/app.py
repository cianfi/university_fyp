from fastapi import FastAPI, Request
import requests
import json
from models import LLMQuery, GrafanaMessage

api = FastAPI()


@api.get("/")
def read_root():
    return {"Hello": "World"}


@api.post("/llm")
def llm(question: str):
    response = requests.request(
        "POST",
        url="http://localhost:11434/api/generate",
        data={
            "model": "phi3:mini",
            "prompt": f"{question}",
            "stream":False
        }
    )
    if response.status_code >= 200 and response.status_code > 300:
        print(response.status_code)
        print(response.text)
    else:
        print(f"Unsuccessful response from LLM. {response.status_code}")


@api.post("/alert")
async def alerts(payload: GrafanaMessage):
    counter = 0

    if payload.status == "firing":
        if counter == 0: 
            #Call function to call LLM 
            print(payload.commonAnnotations["description"])
            counter += 1
        if counter >= 1:
            return "Already working with LLM."

    elif payload.status == "resolved":
        # Need to figure out if I can cancel / notify the LLM to stop if not already.
        print("Resolved")
        counter = 0