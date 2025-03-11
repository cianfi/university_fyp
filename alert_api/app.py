from fastapi import FastAPI, Request
import requests
import json
from models import LLMQuery, PostTest, GrafanaMessage

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

@api.post("/post-test")
async def post_test(test_data: PostTest):
    print(test_data)
    fp = "./alert_api/test_post.json"
    with open(fp, "r") as file:
        data = json.load(file)

    data.append({"name": test_data.user, "age": test_data.age})
    with open(fp, "w") as file:
        json.dump(data, file, indent=4)


@api.post("/alert")
async def alerts(payload: GrafanaMessage):
    if payload.status == "firing":
        # This needs to call the LLM API
        pass
    elif payload.status == "resolved":
        # Need to figure out if I can cancel / notify the LLM to stop if not already.
        pass