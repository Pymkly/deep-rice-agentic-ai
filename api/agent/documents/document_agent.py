import asyncio
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from api.agent.GeminiAgent import GeminiAgent
from api.agent.main_agent import vector_to_str
from api.database.conn import get_con
from api.utlis.deeprice_utils import to_markdown


class DocumentAgent(GeminiAgent):
    def __init__(self):
        super().__init__(
            file_path=os.getenv("DOCUMENT_PROMPT"),
            tag="document"
        )
        self.model = SentenceTransformer("all-mpnet-base-v2")
        self.top_k = 5

    def answer(self, prompt):
        con = get_con()
        cursor = con.cursor()
        documents = self.retrieve(prompt, cursor)
        content = to_markdown(documents)
        params = {
            "user_input": prompt,
            "documents": content
        }
        response = self.invoke_prompt(params, os.getenv("RAG_PROMPT"))
        cursor.close()
        con.close()
        return response

    def retrieve(self, prompt, cursor):
        vector = self.model.encode([prompt]).tolist()[0]
        vector_str = vector_to_str(vector)
        cursor.execute("SELECT content, embedding <-> %s::vector as distance FROM documents order by distance limit %s", (vector_str, self.top_k))
        results = cursor.fetchall()
        contexts = [{"context": context, "distance": distance} for context, distance in results]
        return contexts

    def ingest_directory_to_db(self, path_dir):
        conn = get_con()
        cursor = conn.cursor()
        documents = os.listdir(path_dir)
        for document in documents:
            path = os.path.join(path_dir, document)
            print(path)
            try :
                self.ingest_to_db(path, cursor)
                conn.commit()
            except Exception as e:
                print(e)
            print("done")
        cursor.close()
        conn.close()

    def ingest_to_db(self, path, cursor):
        chunks_processed = self.process(path)
        for chunk in chunks_processed:
            query = """
            INSERT INTO documents (content, embedding, type_document) VALUES (%s, %s::vector, %s)
            """
            vector = chunk["embedding"].tolist()
            embedding_ = vector_to_str(vector)
            cursor.execute(query, (chunk["text"], embedding_, "pdf"))


    def process(self, path):
        chunks = self.split(path)
        datas = []
        for chunk in chunks:
            text = chunk.metadata['extra']
            text += f"page : {chunk.metadata['page']}"
            text += chunk.page_content
            datas.append(text)
        embeddings = self.model.encode(datas)
        return [{
            "text": datas[i],
            "embedding": embeddings[i]
        } for i in range(len(embeddings))]

    def get_title(self, content):
        print(content)
        params = {
            "user_input": content,
        }
        return self.invoke(params)

    def split(self, path):
        pages = asyncio.run(self.load_pdf(path))
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=102)
        documents = text_splitter.split_documents(pages)
        return documents


    async def load_pdf(self, file_path):
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        if pages[0].page_content == "":
            raise Exception("Empty page")
        title = self.get_title(pages[0].page_content)
        processed_documents = []
        for page in pages:
            metadata = page.metadata.copy()
            metadata['extra'] = title
            processed_documents.append(
                Document(page_content=page.page_content,metadata=metadata)
            )
        return processed_documents