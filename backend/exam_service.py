from __future__ import annotations

import math
import random
from dataclasses import dataclass
from fractions import Fraction

from backend.error_taxonomy import (
    CANONICAL_ERROR_TO_TOPIC,
    CANONICAL_ERROR_TYPES,
    DEFAULT_ERROR_TARGETS_BY_TOPIC,
    normalize_error_type,
    topic_for_error_type,
)

ERROR_TO_TOPIC = CANONICAL_ERROR_TO_TOPIC
DEFAULT_ERROR_TARGETS = DEFAULT_ERROR_TARGETS_BY_TOPIC


@dataclass
class GeneratedExamItem:
    position: int
    topic: str
    difficulty: str
    target_error_type: str
    target_concept_tag: str | None
    question_text: str
    answer_format: str
    correct_answer_json: dict
    grading_rubric_json: dict
    validator_notes_json: dict


def topic_for_error(error_type: str) -> str | None:
    return topic_for_error_type(error_type)


def choose_auto_targets(
    *,
    candidate_errors: list[str],
    topics: list[str],
) -> list[str]:
    topic_set = set(topics)
    filtered: list[str] = []
    seen: set[str] = set()
    for error in candidate_errors:
        canonical = normalize_error_type(error)
        if not canonical or canonical in seen:
            continue
        if topic_for_error(canonical) not in topic_set:
            continue
        filtered.append(canonical)
        seen.add(canonical)
    if filtered:
        return filtered

    defaults: list[str] = []
    for topic in topics:
        defaults.extend(DEFAULT_ERROR_TARGETS.get(topic, []))
    return defaults or DEFAULT_ERROR_TARGETS["algebra"]


def generate_exam_items(
    *,
    pack_size: int,
    topics: list[str],
    target_errors: list[str],
    seed: int | None = None,
) -> list[GeneratedExamItem]:
    rng = random.Random(seed)
    normalized_topics = topics or ["algebra", "fractions"]
    normalized_targets: list[str] = []
    for target in target_errors:
        canonical = normalize_error_type(target)
        if canonical and canonical not in normalized_targets:
            normalized_targets.append(canonical)
    if not normalized_targets:
        normalized_targets = choose_auto_targets(candidate_errors=[], topics=normalized_topics)
    targeted_count = int(round(pack_size * 0.7))
    targeted_count = min(pack_size, max(1, targeted_count))

    difficulties = _difficulty_schedule(pack_size)
    items: list[GeneratedExamItem] = []

    for position in range(1, pack_size + 1):
        difficulty = difficulties[position - 1]
        if position <= targeted_count:
            error_type = normalized_targets[(position - 1) % len(normalized_targets)]
            topic = topic_for_error(error_type) or normalized_topics[(position - 1) % len(normalized_topics)]
        else:
            topic = normalized_topics[(position - 1) % len(normalized_topics)]
            topic_errors = DEFAULT_ERROR_TARGETS.get(topic, DEFAULT_ERROR_TARGETS["algebra"])
            error_type = topic_errors[(position - 1) % len(topic_errors)]

        if error_type not in CANONICAL_ERROR_TYPES:
            error_type = DEFAULT_ERROR_TARGETS.get(topic, DEFAULT_ERROR_TARGETS["algebra"])[0]

        generated = _generate_question(
            rng=rng,
            position=position,
            topic=topic,
            difficulty=difficulty,
            error_type=error_type,
        )
        items.append(generated)

    return items


def grade_answer(
    *,
    answer_text: str | None,
    answer_format: str,
    correct_answer_json: dict,
) -> tuple[bool, float, str]:
    normalized_answer = _normalize_answer(answer_text)
    if not normalized_answer:
        return False, 0.0, "No answer provided."

    acceptable = [_normalize_answer(str(value)) for value in correct_answer_json.get("acceptable_answers", [])]
    acceptable = [value for value in acceptable if value]
    if not acceptable:
        canonical = _normalize_answer(str(correct_answer_json.get("value", "")))
        if canonical:
            acceptable = [canonical]

    if answer_format in {"numeric", "fraction"}:
        for value in acceptable:
            if _matches_numeric_or_fraction(normalized_answer, value):
                return True, 1.0, "Correct."
        return False, 0.0, "Incorrect. Re-check arithmetic and signs."

    if normalized_answer in acceptable:
        return True, 1.0, "Correct."
    return False, 0.0, "Incorrect. Review the target concept and try again."


def _difficulty_schedule(pack_size: int) -> list[str]:
    easy_count = int(math.floor(pack_size * 0.4))
    hard_count = int(math.ceil(pack_size * 0.2))
    medium_count = pack_size - easy_count - hard_count
    return (["easy"] * easy_count) + (["medium"] * medium_count) + (["hard"] * hard_count)


def _normalize_answer(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().lower().replace(" ", "")


def _matches_numeric_or_fraction(left: str, right: str) -> bool:
    if left == right:
        return True
    try:
        return abs(float(Fraction(left)) - float(Fraction(right))) < 1e-9
    except Exception:
        try:
            return abs(float(left) - float(right)) < 1e-9
        except Exception:
            return False


def _generate_question(
    *,
    rng: random.Random,
    position: int,
    topic: str,
    difficulty: str,
    error_type: str,
) -> GeneratedExamItem:
    if topic == "fractions":
        return _generate_fraction_question(
            rng=rng,
            position=position,
            difficulty=difficulty,
            error_type=error_type,
        )
    return _generate_algebra_question(
        rng=rng,
        position=position,
        difficulty=difficulty,
        error_type=error_type,
    )


def _generate_algebra_question(
    *,
    rng: random.Random,
    position: int,
    difficulty: str,
    error_type: str,
) -> GeneratedExamItem:
    if error_type in {"sign_error", "equation_isolation_error", "distribution_error"}:
        x_value = rng.randint(-8, 12)
        a = rng.randint(2, 9) if difficulty != "hard" else rng.randint(5, 12)
        b = rng.randint(-12, 12)
        c = a * x_value + b
        question = f"Solve for x: {a}x + ({b}) = {c}"
        acceptable = [str(x_value)]
        concept_tag = "linear_equations"
        answer_format = "numeric"
    else:
        # order_of_operations
        a = rng.randint(2, 9)
        b = rng.randint(1, 9)
        c = rng.randint(2, 7)
        d = rng.randint(1, 6)
        value = a * (b + c) - d
        question = f"Evaluate: {a}({b} + {c}) - {d}"
        acceptable = [str(value)]
        concept_tag = "order_of_operations"
        answer_format = "numeric"

    return GeneratedExamItem(
        position=position,
        topic="algebra",
        difficulty=difficulty,
        target_error_type=error_type,
        target_concept_tag=concept_tag,
        question_text=question,
        answer_format=answer_format,
        correct_answer_json={"value": acceptable[0], "acceptable_answers": acceptable},
        grading_rubric_json={"accept_equivalent": True},
        validator_notes_json={"generator": "template_v1"},
    )


def _generate_fraction_question(
    *,
    rng: random.Random,
    position: int,
    difficulty: str,
    error_type: str,
) -> GeneratedExamItem:
    if error_type == "fraction_simplification_error":
        denominator = rng.randint(6, 18)
        numerator = denominator * rng.randint(2, 5)
        base = Fraction(numerator, denominator)
        question = f"Simplify the fraction: {numerator}/{denominator}"
        answer = str(base)
        acceptable = [answer, f"{float(base):.6f}".rstrip("0").rstrip(".")]
        concept_tag = "fraction_simplification"
    elif error_type == "fraction_arithmetic_error":
        a = Fraction(rng.randint(1, 9), rng.randint(2, 9))
        b = Fraction(rng.randint(1, 9), rng.randint(2, 9))
        op = rng.choice(["+", "-", "*"])
        value = a + b if op == "+" else (a - b if op == "-" else a * b)
        question = f"Compute: {a} {op} {b}"
        answer = str(value)
        acceptable = [answer, f"{float(value):.6f}".rstrip("0").rstrip(".")]
        concept_tag = "fraction_arithmetic"
    else:
        # fraction_common_denominator_error
        d1 = rng.randint(3, 9)
        d2 = rng.randint(3, 9)
        while d2 == d1:
            d2 = rng.randint(3, 9)
        a = Fraction(rng.randint(1, d1 - 1), d1)
        b = Fraction(rng.randint(1, d2 - 1), d2)
        value = a + b
        question = f"Add the fractions: {a} + {b}"
        answer = str(value)
        acceptable = [answer, f"{float(value):.6f}".rstrip("0").rstrip(".")]
        concept_tag = "common_denominator"

    return GeneratedExamItem(
        position=position,
        topic="fractions",
        difficulty=difficulty,
        target_error_type=error_type,
        target_concept_tag=concept_tag,
        question_text=question,
        answer_format="fraction",
        correct_answer_json={"value": acceptable[0], "acceptable_answers": acceptable},
        grading_rubric_json={"accept_equivalent": True},
        validator_notes_json={"generator": "template_v1", "difficulty": difficulty},
    )
