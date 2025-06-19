from langchain_core.prompts import ChatPromptTemplate


def get_instruction(_file_path):
    try:
        with open(_file_path, 'r', encoding='utf-8') as fichier:
            contenu = fichier.read()
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{_file_path}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier '{_file_path}': {e}")
    return contenu


class MainAgent :
    def __init__(self, file_path, llm):
        self.file_path = file_path
        self.llm = llm

    def invoke_prompt(self, params, file_path):
        _instruction = get_instruction(file_path)
        _prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                _instruction
            )
            ,
            (
                "human", "{user_input}"
            )
        ])
        chain = _prompt | self.llm
        response = chain.invoke(
            params
        )
        return response.content

    def invoke(self, params):
        return self.invoke_prompt(params, self.file_path)