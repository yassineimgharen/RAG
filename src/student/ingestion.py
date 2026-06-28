from typing import List, Any, Dict
from pathlib import Path


# rglob find everything inside a folder and all subfolders
def find_files(repo_path: str) -> List[str]:
    # Path object gives useful attributes (name, suffix(extention), is_file)
    repo = Path(repo_path)

    return [
        str(path)
        for path in repo.rglob("*")
        if path.is_file() and path.suffix in {".py", ".md"}
    ]


# take one .py file and cut it into chunks
def chunk_python_file(file_path: str, max_chunk_size: int = 2000) -> List[Dict[str, Any]]:
    list_of_chunks = []
    i = 0
    with open(file_path, "r") as file:
        content = file.read()
    while i < len(content):
        one_chunk = {
            "file_path": file_path,
            "first_character_index": i,
            "last_character_index": i + max_chunk_size,
            "text": content[i: i + max_chunk_size]
        }
        i += max_chunk_size
        list_of_chunks.append(one_chunk)
    return list_of_chunks
