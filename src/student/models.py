import uuid
from typing import List
from pydantic import ConfigDict, Field, BaseModel


class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int


# generate random id (550e8400-e29b-41d...) lambda each generate a new id
class UnansweredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    model_config = ConfigDict(extra="ignore")
    sources: List[MinimalSource]
    answer: str


# UnansweredQuestions → "here are questions, go find the answers"
# AnsweredQuestions   → "here are the correct answers, check yourself"
class RagDataset(BaseModel):
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


# search results for one question
class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    answer: str


# number of results per question
class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    search_results: List[MinimalAnswer]
