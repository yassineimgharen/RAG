import os
from typing import List
import uuid
import torch

from tqdm import tqdm
from src.student.models import MinimalAnswer, MinimalSource
from src.student.models import StudentSearchResultsAndAnswer
from src.student.models import StudentSearchResults
from transformers import AutoModelForCausalLM, AutoTokenizer
from student import retrieval


# tokenizer → converts text to numbers (tokens) that the model understands
# model     → the actual Qwen brain that generates answers
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B").to(device)


def generate_answer(question_id: str,
                    question: str,
                    retrieved_sources: List[MinimalSource]
                    ) -> MinimalAnswer:
    context_texts: str = ""
    max_context = 4000
    for i, source in enumerate(retrieved_sources):
        with open(source.file_path, "r", encoding="utf-8",
                  errors="ignore") as f:
            text = f.read()
        chunk_text = text[source.first_character_index:
                          source.last_character_index]
        if len(context_texts) + len(chunk_text) > max_context:
            break
        context_texts += (
            f"chunk {i + 1} extracted from "
            f"the file{source.file_path}:\n{chunk_text}\n\n"
        )

    system_prompt = (
        "You are a helpful assistant. Answer the question using ONLY "
        "the provided context.\n"
        "If the context does not contain the answer, say \"I cannot "
        "answer based on the provided context.\"\n"
        "Always answer in a complete sentence. "
        "Be concise and factual. Do not invent information."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: "
                                    f"{context_texts}\n\nQuestion: {question}"}
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False)
    inputs = tokenizer(prompt, return_tensors="pt",
                       truncation=True, max_length=2048).to(device)
    input_len = inputs["input_ids"].shape[1]
    outputs = model.generate(
        **inputs, max_new_tokens=80, do_sample=False)
    answer_text = tokenizer.decode(
        outputs[0][input_len:], skip_special_tokens=True)
    return MinimalAnswer(
        question_id=question_id,
        question=question,
        retrieved_sources=[s.model_dump() for s in retrieved_sources],
        answer=answer_text
    )


def answer(question: str, k: int = 10) -> None:
    sources = retrieval.search(question, k)
    question_id = str(uuid.uuid4())
    result = generate_answer(question_id, question, sources)
    print(result.answer)


def answer_dataset(
    student_search_results_path: str,
    save_directory: str
) -> None:
    with open(student_search_results_path, "r") as f:
        student_results = StudentSearchResults.model_validate_json(f.read())

    answers = []
    for result in tqdm(student_results.search_results,
                       desc="Generating answers"):
        answer = generate_answer(
            question_id=result.question_id,
            question=result.question,
            retrieved_sources=result.retrieved_sources
        )
        answers.append(answer)

    output = StudentSearchResultsAndAnswer(
        search_results=answers,
        k=student_results.k
    )
    filename = os.path.basename(student_search_results_path)
    save_path = os.path.join(save_directory, filename)
    with open(save_path, "w") as f:
        f.write(output.model_dump_json(indent=2))
    print(f"Saved to {save_path}")
