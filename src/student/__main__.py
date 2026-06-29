import fire
from student import ingestion
from student import retrieval


class Student:
    def index(self, max_chunk_size: int = 2000) -> None:
        """Index the vLLM repository."""
        ingestion.index(max_chunk_size)

    def search(self, question: str, k: int = 5) -> None:
        """Search for a single query."""
        results = retrieval.search(question, k)
        for source in results:
            print(source)


if __name__ == "__main__":
    fire.Fire(Student)
