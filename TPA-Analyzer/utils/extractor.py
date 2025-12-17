from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from utils.schema import TPAMetadata
from typing import List, Optional
import logging

import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
groq_api_key = os.getenv("GROQ_API_KEY")

def extract_metadata(documents, max_chunks: int = 5, chunk_size: int = 2000):
    """
    Extract metadata from TPA documents.
    
    Args:
        documents: Input documents to analyze
        max_chunks: Maximum number of chunks to process (cost control)
        chunk_size: Size of each text chunk
    
    Returns:
        TPAMetadata object with extracted information
    """
    
    if not documents:
        raise ValueError("No documents provided for analysis")
    
    # Larger chunks to capture more context
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=300,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_documents(documents)
    
    if not chunks:
        raise ValueError("Document splitting resulted in no chunks")
    
    logger.info(f"Split document into {len(chunks)} chunks")

    # Process strategic chunks: beginning, middle, end
    strategic_chunks = _select_strategic_chunks(chunks, max_chunks)

    parser = PydanticOutputParser(pydantic_object=TPAMetadata)

    prompt = PromptTemplate(
        template="""You are an expert contract analyst specializing in Third Party Administrator (TPA) agreements.

Carefully extract the following metadata from the provided TPA agreement text. Be thorough and accurate.

{format_instructions}

Important instructions:
- Extract exact values as they appear in the document
- For dates, use ISO format (YYYY-MM-DD) if possible
- For monetary values, include currency
- If a field is not found in this section, return null
- Return ONLY valid JSON, no markdown, no explanations

TPA Agreement Text:
{context}
""",
        input_variables=["context"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",  # More reliable than gpt-oss
        temperature=0,
        groq_api_key=groq_api_key,
        max_retries=2
    )

    chain = prompt | llm | parser

    # Extract metadata from multiple chunks and merge
    results = []
    for i, chunk in enumerate(strategic_chunks):
        try:
            logger.info(f"Processing chunk {i+1}/{len(strategic_chunks)}")
            result = chain.invoke({"context": chunk.page_content})
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing chunk {i}: {str(e)}")
            continue
    
    if not results:
        raise RuntimeError("Failed to extract metadata from any chunk")
    
    # Merge results with priority to first non-null value
    final_metadata = _merge_metadata(results)
    
    return final_metadata


def _select_strategic_chunks(chunks: List, max_chunks: int) -> List:
    """
    Select the most relevant chunks for metadata extraction.
    Prioritizes beginning (contract details) and end (signatures/dates).
    """
    if len(chunks) <= max_chunks:
        return chunks
    
    # Take first chunks (header info), some middle, and last chunks (signature/dates)
    num_start = max(2, max_chunks // 2)
    num_end = max(1, max_chunks // 4)
    num_middle = max_chunks - num_start - num_end
    
    middle_idx = len(chunks) // 2
    
    selected = (
        chunks[:num_start] + 
        chunks[middle_idx:middle_idx + num_middle] + 
        chunks[-num_end:]
    )
    
    return selected


def _merge_metadata(results: List[TPAMetadata]) -> TPAMetadata:
    """
    Merge multiple metadata extractions, prioritizing non-null values.
    First occurrence wins for conflicts.
    """
    if len(results) == 1:
        return results[0]
    
    merged = results[0].model_copy(deep=True)
    
    for result in results[1:]:
        for field_name, field_value in result.model_dump().items():
            current_value = getattr(merged, field_name)
            
            # Update if current is null but new value exists
            if current_value is None and field_value is not None:
                setattr(merged, field_name, field_value)
            
            # For list fields, combine unique values
            elif isinstance(current_value, list) and isinstance(field_value, list):
                combined = list(set(current_value + field_value))
                setattr(merged, field_name, combined)
    
    return merged