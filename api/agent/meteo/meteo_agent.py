import os
from datetime import datetime

from dotenv import load_dotenv

from api.agent.GeminiAgent import GeminiAgent
from api.agent.meteo.open_meteo import OpenMeteo

load_dotenv()

class MeteoAgent(GeminiAgent):
	def __init__(self):
		super().__init__(
			file_path=os.getenv("METEO_PROMPT")
		)
		self.open_meteo = OpenMeteo()
		self.tools = [
			self.open_meteo.get_temperature,
			self.open_meteo.get_rain,
			self.open_meteo.get_soil_info,
			self.open_meteo.get_visibility,
		]

	def ask_actions(self, prompt):
		params = {
			"user_input" : prompt,
		}
		actions = self.invoke_prompt(params, "prompt/meteo/tools.txt")
		indexes = actions.split(',')
		return [int(index) for index in indexes]

	def get_meteo(self, prompt, longitude, latitude):
		actions = self.ask_actions(prompt)
		infos = [self.tools[action](longitude, latitude) for action in actions ]
		return "\n".join(infos)

	def answer(self, prompt, longitude, latitude):
		date = datetime.now()
		# print(info)
		meteo = self.get_meteo(prompt, longitude, latitude)
		params = {
			"user_input": prompt,
			"date" : date,
			"meteo" : meteo,
			"additionnal_info" : ""
		}
		return self.invoke(params)
