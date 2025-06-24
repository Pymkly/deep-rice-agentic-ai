from api.agent.orchestration.orchestrator_agent import OrchestratorAgent

agent= OrchestratorAgent()
prompt = "Bonjour. Que devrais-je savoir sur la maladie du pyriculariose ?"
response = agent.answer(prompt, [])
print(f"Question: {prompt}")
print(f"Réponse : {response}")