from fastapi import FastAPI
from models import LLMQuery, GrafanaMessage, APILLMQuery
from ai_agent import Agent

api = FastAPI()
chat_agent = Agent()

@api.get("/")
def read_root():
    return {"Hello": "World"}


@api.post("/llm")
def llm(question: APILLMQuery):
    llm_question = LLMQuery(question=question.question)
    response = chat_agent.alert(llm_message=llm_question)
    return response

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