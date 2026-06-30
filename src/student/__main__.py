import fire
from student import generation, ingestion
from student import retrieval, evaluation


class Student:

    def index(self, max_chunk_size: int = 2000) -> None:
        """Index the vLLM repository."""
        try:
            ingestion.index(max_chunk_size)
        except Exception as e:
            print(f"Error during indexing: {e}")

    def search(self, question: str = "", k: int = 5) -> None:
        try:
            if not question.strip():
                print("Error: question cannot be empty")
                return
            if k < 1:
                print("Error: k must be >= 1")
                return
            results = retrieval.search(question, k)
            for source in results:
                print(source)
        except Exception as e:
            print(f"Error during search: {e}")

    def search_dataset(self, dataset_path: str,
                       save_directory: str,
                       k: int = 10) -> None:
        try:
            retrieval.search_dataset(dataset_path, save_directory, k)
        except Exception as e:
            print(f"Error during search_dataset: {e}")

    def evaluate(self,
                 student_results_path: str,
                 ground_truth_path: str,
                 k: int = 10
                 ) -> None:
        try:
            evaluation.evaluate(student_results_path,
                                ground_truth_path, k)
        except Exception as e:
            print(f"Error during evaluation: {e}")

    def answer(self, question: str = "", k: int = 10) -> None:
        try:
            if not question.strip():
                print("Error: question cannot be empty")
                return
            generation.answer(question, k)
        except Exception as e:
            print(f"Error during answer: {e}")

    def answer_dataset(self,
                       student_search_results_path: str,
                       save_directory: str
                       ) -> None:
        try:
            generation.answer_dataset(student_search_results_path,
                                      save_directory)
        except Exception as e:
            print(f"Error during answer_dataset: {e}")


if __name__ == "__main__":
    fire.Fire(Student)
