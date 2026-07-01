import os

import fire
from student import generation, ingestion
from student import retrieval, evaluation


class Student:

    def index(self, max_chunk_size: int = 2000) -> None:
        """Index the vLLM repository."""
        try:
            if max_chunk_size < 1 or max_chunk_size > 2000:
                print("Error: max_chunk_size must be between 1 and 2000")
                return
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
            if k < 1:
                print("Error: k must be >= 1")
                return
            retrieval.search_dataset(dataset_path, save_directory, k)
        except Exception as e:
            print(f"Error during search_dataset: {e}")

    def evaluate(self,
                 student_results_path: str,
                 ground_truth_path: str,
                 k: int = 10
                 ) -> None:
        try:
            if k < 1:
                print("Error: k must be >= 1")
                return
            evaluation.evaluate(student_results_path,
                                ground_truth_path, k)
        except Exception as e:
            print(f"Error during evaluation: {e}")

    def answer(self, question: str = "", k: int = 10) -> None:
        try:
            if not question.strip():
                print("Error: question cannot be empty")
                return
            if k < 1:
                print("Error: k must be >= 1")
                return
            generation.answer(question, k)
        except Exception as e:
            print(f"Error during answer: {e}")

    def answer_dataset(self,
                       student_search_results_path: str,
                       save_directory: str
                       ) -> None:
        try:
            if not os.path.exists(save_directory):
                os.makedirs(save_directory, exist_ok=True)
            generation.answer_dataset(student_search_results_path,
                                      save_directory)
        except Exception as e:
            print(f"Error during answer_dataset: {e}")


if __name__ == "__main__":
    fire.Fire(Student)
