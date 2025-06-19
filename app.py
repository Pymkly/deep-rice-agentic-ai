from api.agent.meteo.meteo_agent import MeteoAgent

meteo_agent = MeteoAgent()
prompt = "a quel heur la pluie va tomber et a quel heur la temperature atteindra son maximum aujourd hui"
response = meteo_agent.answer(prompt, 45.84308675616946, -18.346497123728852)
print(response)
