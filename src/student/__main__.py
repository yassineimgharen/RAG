import fire
from student import ingestion


class Student:
    def index(self, max_chunk_size: int = 2000) -> None:
        """Index the vLLM repository."""
        ingestion.index(max_chunk_size)


if __name__ == "__main__":
    fire.Fire(Student)
