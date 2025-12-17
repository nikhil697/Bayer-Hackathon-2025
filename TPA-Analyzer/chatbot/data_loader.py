import pandas as pd

def load_excel_as_texts(excel_path: str):
    df = pd.read_excel(excel_path)

    texts = []
    for _, row in df.iterrows():
        content = "\n".join(
            f"{col}: {row[col]}"
            for col in df.columns
            if pd.notna(row[col])
        )
        texts.append(content)

    return texts