import fire
from student import generation, ingestion
from student import retrieval, evaluation


class Student:
    def index(self, max_chunk_size: int = 2000) -> None:
        """Index the vLLM repository."""
        ingestion.index(max_chunk_size)

    def search(self, question: str, k: int = 5) -> None:
        """Search for a single query."""
        results = retrieval.search(question, k)
        for source in results:
            print(source)

    def search_dataset(self, dataset_path: str,
                       save_directory: str,
                       k: int = 10) -> None:
        retrieval.search_dataset(dataset_path, save_directory, k)

    def evaluate(self,
                 student_results_path: str,
                 ground_truth_path: str,
                 k: int = 10
                 ) -> None:
        evaluation.evaluate(student_results_path, ground_truth_path, k)

    def answer(self, question: str, k: int = 10) -> None:
        generation.answer(question, k)

    def answer_dataset(self,
                       student_search_results_path: str,
                       save_directory: str
                       ) -> None:
        generation.answer_dataset(student_search_results_path, save_directory)


if __name__ == "__main__":
    fire.Fire(Student)
