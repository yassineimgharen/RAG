from typing import List, Any, Dict
from pathlib import Path
from tqdm import tqdm
import bm25s
import pickle
import json


# rglob find everything inside a folder and all subfolders
def find_files(repo_path: str) -> List[str]:
    # Path object gives useful attributes (name, suffix(extention), is_file)
    try:
        repo = Path(repo_path)
        return [
            str(path)
            for path in repo.rglob("*")
            if path.is_file() and path.suffix in {".py", ".md"}
        ]
    except Exception as e:
        print(f"Error finding files in {repo_path}: {e}")
        return []


# take one .py file and cut it into chunks
def chunk_python_file(
            file_path: str,
            max_chunk_size: int = 2000
) -> List[Dict[str, Any]]:
    try:
        list_of_chunks = []
        i = 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
        while i < len(content):
            one_chunk = {
                "file_path": file_path,
                "first_character_index": i,
                "last_character_index": min(i + max_chunk_size, len(content)),
                "text": content[i: i + max_chunk_size]
            }
            i += max_chunk_size
            list_of_chunks.append(one_chunk)
        return list_of_chunks
    except Exception as e:
        print(f"Error chunking {file_path}: {e}")
        return []


def chunk_md_file(file_path: str,
                  max_chunk_size: int = 2000) -> List[Dict[str, Any]]:
    try:
        list_of_chunks = []
        i = 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        while i < len(content):
            one_chunk = {
                "file_path": file_path,
                "first_character_index": i,
                "last_character_index": min(i + max_chunk_size, len(content)),
                "text": content[i: i + max_chunk_size]
            }
            list_of_chunks.append(one_chunk)
            i += max_chunk_size
        return list_of_chunks
    except Exception as e:
        print(f"Error chunking {file_path}: {e}")
        return []


def build_index(all_chunks: List[Dict[str, Any]]) -> bm25s.BM25:
    try:
        retriever = bm25s.BM25()
        corpus = [ele.get("text") for ele in all_chunks]
        tokenized = bm25s.tokenize(corpus)
        retriever.index(tokenized)
        return retriever
    except Exception as e:
        print(f"Error building index: {e}")
        raise


def save_chunks(chunks: List[Dict[str, Any]], save_path: str) -> None:
    try:
        with open(save_path, "w") as f:
            json.dump(chunks, f, indent=2)
    except Exception as e:
        print(f"Error saving chunks to {save_path}: {e}")


def save_index(retriever: bm25s.BM25, save_path: str) -> None:
    try:
        with open(save_path, "wb") as f:
            pickle.dump(retriever, f)
    except Exception as e:
        print(f"Error saving index to {save_path}: {e}")


def index(max_chunk_size: int = 2000) -> None:
    repo_path = "data/raw/vllm-0.10.1"
    chunks_path = "data/processed/chunks/chunks.json"
    index_path = "data/processed/bm25_index/index.pkl"

    all_chunks = []
    files = find_files(repo_path)

    for file in tqdm(files, desc="Chunking files"):
        if file.endswith(".py"):
            all_chunks += (chunk_python_file(file, max_chunk_size))
        else:
            all_chunks += (chunk_md_file(file, max_chunk_size))

    retriever = build_index(all_chunks)
    save_chunks(all_chunks, chunks_path)
    save_index(retriever, index_path)

    print("Ingestion complete! Indices saved under data/processed/")
