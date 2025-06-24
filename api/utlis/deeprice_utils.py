import pandas as pd


def to_markdown(data):
    df = pd.DataFrame(data)
    contexte = df.to_markdown(index=False)
    return contexte