from typing import Dict, Any, List
import pickle
import json
import bm25s
from student.models import MinimalSource
from student.models import RagDataset, MinimalSearchResults
from student.models import StudentSearchResults
from tqdm import tqdm
import os


def load_chunks(file_path: str) -> List[Dict[str, Any]]:
    try:
        with open(file_path, "r") as f:
            chunks = json.load(f)
        return chunks
    except Exception as e:
        print(f"Error loading chunks from {file_path}: {e}")
        raise


def load_index(file_path: str) -> bm25s.BM25:
    try:
        with open(file_path, "rb") as f:
            retriever = pickle.load(f)
        return retriever
    except Exception as e:
        print(f"Error loading index from {file_path}: {e}")
        raise


# takes question + k → returns List[MinimalSource]
def search(question: str, k: int = 5) -> List[MinimalSource]:
    try:
        chunks = load_chunks("data/processed/chunks/chunks.json")
        retriever = load_index("data/processed/bm25_index/index.pkl")
        tokenized_query = bm25s.tokenize(question)
        results, scores = retriever.retrieve(tokenized_query, k=k)
        # topk chunks fin n9dr l9a ljawab
        sources = []
        for idx in results[0]:
            chunk = chunks[idx]
            source = MinimalSource(
                file_path=chunk["file_path"],
                first_character_index=chunk["first_character_index"],
                last_character_index=chunk["last_character_index"]
            )
            sources.append(source)
        return sources
    except Exception as e:
        print(f"Error during search: {e}")
        return []


# takes a dataset JSON file and searches for every question in it.
# and save it to a file
def search_dataset(
    dataset_path: str,
    save_directory: str,
    k: int = 10
) -> None:
    try:
        with open(dataset_path, "r") as f:
            dataset_json = f.read()
        dataset = RagDataset.model_validate_json(dataset_json)
        results = []
        for question in tqdm(dataset.rag_questions, desc="Searching dataset"):
            sources = search(question.question, k)
            result = MinimalSearchResults(
                question_id=question.question_id,
                question=question.question,
                retrieved_sources=sources
            )
            results.append(result)
        output = StudentSearchResults(search_results=results, k=k)
        # jib gha file name mn fullpath
        filename = os.path.basename(dataset_path)
        save_path = os.path.join(save_directory, filename)
        with open(save_path, "w") as f:
            f.write(output.model_dump_json(indent=2))
        print(f"Saved to {save_path}")
    except Exception as e:
        print(f"Error during search_dataset: {e}")
