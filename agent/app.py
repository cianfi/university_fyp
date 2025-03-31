from fastapi import FastAPI
from agent.models import LLMQuery, GrafanaMessage, APILLMQuery
from agent.ai_agent import Agent

from datetime import datetime


api = FastAPI()
agent = Agent()
script_running = 0
start_time = datetime.now()

@api.get("/")
def read_root():
    return {"Hello": "World"}


@api.post("/llm")
def llm(question: APILLMQuery):
    llm_question = LLMQuery(question=question.question)
    response = agent.alert(alert_description=llm_question)
    return response

@api.post("/alert")
async def alerts(payload: GrafanaMessage):
    global script_running 
    global start_time

    # Change between BGP issue and OSPF issue. Need to figure out why OSPF alerts when there is no data / suppress it.
    # Need to figure out why BGP alerts have two instances for the same alert.

    if payload.status == "firing":
        if script_running == 0: 
            script_running += 1
            print(f"[{script_running}] Alert received and processing.")
            agent.alert(alert_description=payload.commonAnnotations["description"])
            return {"message": "Alert received and processing."}
        elif script_running >= 1:
            return {"message": "Alert already being processed."}

    elif payload.status == "resolved":
        script_running = 0
        time_taken = datetime.now() - start_time
        minuutes, seconds = divmod(time_taken.seconds, 60)
        print(f"[{script_running}] Alert resolved. Time taken: {minuutes} min(s) {seconds} sec(s)")
        return {"message": "Alert resolved."}
        