from fastapi import FastAPI
from models import LLMQuery, GrafanaMessage, APILLMQuery
from ai_agent import Agent

from datetime import datetime

api = FastAPI()
agent = Agent()
script_running = 0
start_time = datetime.now()

@api.post("/llm")
def llm(question: APILLMQuery):
    """
    This is just a basic API endpoint that will be used to test the LLM.

    arg:
        question: APILLLMQuery: The question that will be sent to the llm
    return:
        dict: The response that will be sent to Grafana
    """
    llm_question = LLMQuery(question=question.question)
    response = agent.alert(alert_description=llm_question)
    return response

@api.post("/alert")
async def alerts(payload: GrafanaMessage):
    """
    This is the webhook callback that will be called by Grafana when an alert is triggered.

    arg:
        payload: GrafanaMessage: The payload that will be sent by Grafana

    return:
        dict: The response that will be sent to Grafana
    """
    global script_running 
    global start_time

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
        return {"message": "Alert resolved."}
        