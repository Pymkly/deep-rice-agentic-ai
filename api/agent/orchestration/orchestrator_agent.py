import pandas as pd
from dotenv import load_dotenv
import os

from api.agent.GeminiAgent import GeminiAgent
from api.agent.meteo.meteo_agent import MeteoAgent
from api.agent.usual.usual_agent import UsualAgent

load_dotenv()

class OrchestratorAgent(GeminiAgent):
    def __init__(self):
        super().__init__(
			file_path=os.getenv("ORCHESTRATOR_AGENT_PROMPT"),
            tag="orchestration"
		)
        self.agents = [
            UsualAgent(),
            MeteoAgent()
        ]

    def answer(self, prompt):
        responses = self.agents_responses(prompt)
        return self.gather_response(prompt, responses)

    def gather_response(self, prompt, responses):
        df = pd.DataFrame(responses)
        agent_responses = df.to_markdown(index=False)
        print(agent_responses)
        params = {
            "user_input": prompt,
            "agent_responses" : agent_responses
        }
        return self.invoke_prompt(params, os.getenv("ORCHESTRATOR_AGENT_GATHER_PROMPT"))

    def agents_responses(self, prompt):
        agents = self.get_agents_concerned(prompt)
        responses = []
        for line in agents:
            agent = line["agent"]
            question = line["question"]
            if agent.tag == "meteo" :
                resp = agent.answer(question, 45.84308675616946, -18.346497123728852)
            else:
                resp = agent.answer(question)
            responses.append({
                "agent": agent.tag,
                "question": question,
                "response": resp
            })
        return responses

    def get_agents_concerned(self, prompt):
        params = {
            "user_input": prompt,
        }
        response = self.invoke(params)
        lines = response.splitlines()
        return self.get_agents(lines)

    def get_agents(self, lines):
        response = []
        for line in lines:
            temp = line.split("#")
            index = int(temp[0])
            question = line[2:]
            agent = self.agents[index]
            response.append({
                "question": question,
                "agent": agent
            })
        return response