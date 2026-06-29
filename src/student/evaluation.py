from student.models import MinimalSource, RagDataset, StudentSearchResults


# same file + at least 5% shared characters = found
def calculate_overlap(my_source: MinimalSource,
                      correct_source: MinimalSource
                      ) -> bool:
    if my_source.file_path != correct_source.file_path:
        return False
    overlap_start = max(my_source.first_character_index,
                        correct_source.first_character_index)
    overlap_end = min(my_source.last_character_index,
                      correct_source.last_character_index)
    overlap = overlap_end - overlap_start
    if overlap <= 0:
        return False
    correct_size = (correct_source.last_character_index
                    - correct_source.first_character_index)
    percentage = overlap / correct_size
    return percentage >= 0.05


# "Did any of my top-k sources overlap with the correct source?
# Check if your top-k chunks contain the correct answer
# how many of your sources to check
def recall_at_k(retrieved_sources: list[MinimalSource],
                correct_sources: list[MinimalSource],
                k: int) -> float:
    if k > len(retrieved_sources):
        k = len(retrieved_sources)
    retrieved_sources = retrieved_sources[:k]
    correct_count = 0
    for correct_source in correct_sources:
        for my_source in retrieved_sources:
            if calculate_overlap(my_source, correct_source):
                correct_count += 1
                break
    return correct_count / len(correct_sources)


def evaluate(student_results_path: str,
             ground_truth_path: str,
             k: int = 10) -> None:
    with open(student_results_path, "r") as f:
        student_results = StudentSearchResults.model_validate_json(f.read())

    with open(ground_truth_path, "r") as f:
        ground_truth = RagDataset.model_validate_json(f.read())

    gt_dict = {}
    for question in ground_truth.rag_questions:
        gt_dict[question.question_id] = question.sources

    for k_val in [1, 3, 5, 10]:
        scores = []
        for result in student_results.search_results:
            correct_sources = gt_dict[result.question_id]
            score = recall_at_k(result.retrieved_sources,
                                correct_sources, k_val)
            scores.append(score)
        recall = sum(scores) / len(scores)
        print(f"Recall@{k_val}: {recall:.3f}")
