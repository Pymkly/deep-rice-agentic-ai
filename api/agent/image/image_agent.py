import os

import pandas as pd
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from api.agent.GeminiAgent import GeminiAgent
from api.agent.main_agent import vector_to_str
from api.database.conn import get_con
from api.utlis.deeprice_utils import to_markdown


def embed(path):
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    # Load and preprocess the image
    image = Image.open(path)  # Replace with your image path
    inputs = processor(images=image, return_tensors="pt")
    # Generate the image embedding
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)
    # Normalize the embedding
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    return image_features[0]


def process_image(curr, path, context):
    print("embedding....")
    vector = embed(path)
    print("image embedded...")
    vector_str = vector_to_str(vector.tolist())
    print("save image ...........")
    curr.execute(
        "insert into image_embedded(context, embedding) values (%s, %s::vector)",
        (context, vector_str),
    )
    print("image saved")

def process_images_on_dir(curr, path, context):
    images = os.listdir(path)
    paths = [os.path.join(path, image) for image in images]
    i = 1
    for path in paths:
        print(i)
        process_image(curr, path, context)
        i+=1

def get_images_near(curr, path, top_k, index):
    print("embedding....")
    vector = embed(path)
    print("image embedded...")
    vector_str = vector_to_str(vector.tolist())
    query = """
        SELECT context, embedding <-> %s::vector AS distance
        FROM image_embedded
        ORDER BY distance
        LIMIT %s;
    """
    curr.execute(query, (vector_str, top_k))
    results = curr.fetchall()
    contexts = [{"context":context, "distance" : distance, "index" : index} for context, distance in results]
    return contexts

def get_images_near_wcon(path, top_k):
    conn = get_con()
    cur = conn.cursor()
    contexts = get_images_near(cur, path, top_k, 1)
    cur.close()
    conn.close()
    return contexts

class ImageAgent(GeminiAgent):
    def __init__(self, top_k):
        super().__init__(
            tag="image",
            file_path=os.getenv("IMAGE_PROMPT")
        )
        self.top_k = top_k

    def get_near(self, paths):
        conn = get_con()
        cur = conn.cursor()
        results = []
        i = 1
        for path in paths:
            contexts = get_images_near(cur, path, self.top_k, i)
            results.extend(contexts)
        cur.close()
        conn.close()
        return results

    def answer(self, prompt, paths):
        data = self.get_near(paths)
        contexte = to_markdown(data)
        params = {
            "user_input": prompt,
            "contexte_similaire" : contexte
        }
        return self.invoke(params)