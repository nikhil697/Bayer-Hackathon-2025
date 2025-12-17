from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from utils.schema import TPAMetadata

import os
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

def extract_metadata(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    parser = PydanticOutputParser(pydantic_object=TPAMetadata)

    prompt = PromptTemplate(
        template="""
You are a contract analyst expert.
Extract the following metadata from the TPA agreement.

{format_instructions}

If a field is not present, return null.
Return JSON only.

Text:
{context}
""",
        input_variables=["context"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    llm = ChatGroq(
        # model_name="llama-3.1-70b-versatile",
        model_name="openai/gpt-oss-120b",
        temperature=0,
        groq_api_key=groq_api_key
    )

    chain = prompt | llm | parser

    return chain.invoke({"context": chunks[0].page_content})
