import uuid
from typing import List
from pydantic import Field, BaseModel
from src.student.models import (
    MinimalSource,
    UnansweredQuestion,
    AnsweredQuestion,
    RagDataset,
    MinimalSearchResults,
    MinimalAnswer,
    StudentSearchResults,
    StudentSearchResultsAndAnswer
)

# test MinimalSource
source = MinimalSource(
    file_path="vllm/engine/llm_engine.py",
    first_character_index=1500,
    last_character_index=3200
)
print("MinimalSource:", source)

# test UnansweredQuestion
question = UnansweredQuestion(question="How does vLLM handle memory?")
print("UnansweredQuestion:", question)

# test AnsweredQuestion
answered = AnsweredQuestion(
    question="How does vLLM handle memory?",
    sources=[source],
    answer="vLLM uses PagedAttention..."
)
print("AnsweredQuestion:", answered)

# test RagDataset
dataset = RagDataset(rag_questions=[question, answered])
print("RagDataset:", dataset)

# test JSON saving
print("\nJSON output:")
print(dataset.model_dump_json(indent=2))
