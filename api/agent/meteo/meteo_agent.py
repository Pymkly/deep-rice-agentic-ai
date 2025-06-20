import os
from datetime import datetime

from dotenv import load_dotenv

from api.agent.GeminiAgent import GeminiAgent
from api.agent.meteo.open_meteo import OpenMeteo

load_dotenv()

class MeteoAgent(GeminiAgent):
	def __init__(self):
		super().__init__(
			file_path=os.getenv("METEO_PROMPT"),
			tag="meteo"
		)
		self.open_meteo = OpenMeteo()
		self.tools = [
			['temperature_2m', 'apparent_temperature'],
			['rain', 'precipitation_probability'],
			['soil_temperature_0cm', 'soil_moisture_1_to_3cm'],
			['cloud_cover', 'visibility'],
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
		params = ['date']
		for index in actions:
			for param in self.tools[index]:
				params.append(param)
		infos = self.open_meteo.extract_info(longitude, latitude, params)
		# print(infos)
		return infos

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
