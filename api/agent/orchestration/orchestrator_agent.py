import os

from dotenv import load_dotenv

from api.agent.GeminiAgent import GeminiAgent
from api.agent.documents.document_agent import DocumentAgent
from api.agent.image.image_agent import ImageAgent
from api.agent.meteo.meteo_agent import MeteoAgent
from api.agent.usual.usual_agent import UsualAgent
from api.utlis.deeprice_utils import to_markdown

load_dotenv()

class OrchestratorAgent(GeminiAgent):
    def __init__(self):
        super().__init__(
			file_path=os.getenv("ORCHESTRATOR_AGENT_PROMPT"),
            tag="orchestration"
		)
        self.agents = [
            UsualAgent(),
            MeteoAgent(),
            ImageAgent(top_k=5),
            DocumentAgent()
        ]

    def answer(self, prompt, paths):
        responses = self.agents_responses(prompt, paths,45.84308675616946, -18.346497123728852)
        return self.gather_response(prompt, responses)

    def gather_response(self, prompt, responses):
        agent_responses = to_markdown(responses)
        print(agent_responses)
        params = {
            "user_input": prompt,
            "agent_responses" : agent_responses
        }
        return self.invoke_prompt(params, os.getenv("ORCHESTRATOR_AGENT_GATHER_PROMPT"))

    def agents_responses(self, prompt, path, longitude, latitude):
        agents = self.get_agents_concerned(prompt)
        responses = []
        for line in agents:
            agent = line["agent"]
            question = line["question"]
            if agent.tag == "meteo" :
                resp = agent.answer(question, longitude, latitude)
            elif agent.tag == "image" :
                resp = agent.answer(question, path)
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