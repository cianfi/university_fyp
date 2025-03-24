from fastapi import FastAPI
from models import LLMQuery, GrafanaMessage, APILLMQuery
from ai_agent import Agent

api = FastAPI()
agent = Agent()
script_running = 0

@api.get("/")
def read_root():
    return {"Hello": "World"}


@api.post("/llm")
def llm(question: APILLMQuery):
    llm_question = LLMQuery(question=question.question)
    response = agent.alert(llm_message=llm_question)
    return response

@api.post("/alert")
async def alerts(payload: GrafanaMessage):
    global script_running
    if payload.status == "firing":
        if script_running == 0: 
            agent.alert(llm_message=payload.commonAnnotations["description"])
            script_running += 1
            return {"message": "Alert received and processing."}
        elif script_running >= 1:
            return {"message": "Alert already being processed."}

    elif payload.status == "resolved":
        script_running = 0
        return {"message": "Alert resolved."}
        