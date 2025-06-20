import os

from dotenv import load_dotenv

from api.agent.GeminiAgent import GeminiAgent

load_dotenv()

class UsualAgent(GeminiAgent):
    def __init__(self):
        super().__init__(
            file_path=os.getenv("USUAL_PROMPT"),
            tag="usual"
        )

    def answer(self, prompt):
        params = {
            "user_input": prompt,
        }
        return self.invoke(params)