"""
Verifies that all key attributes from the example input JSON files are correctly
loaded through the parsing pipeline before being sent to the LLM.

These tests do NOT call the LLM — they only exercise the data transformation
layer (module.py helpers → typed objects → prompt string).
"""

import json
import pytest
from pathlib import Path

from lf_toolkit.chat import ChatRequest
from src.agent.utils.parse_json_context_to_prompt import (
    QuestionDetails,
    StudentWorkResponseArea,
    QuestionAccessInformation,
    parse_json_to_prompt,
)
from src.module import (
    _build_question_information,
    _build_submission_summary,
    _build_access_information,
)

EXAMPLE_INPUTS_DIR = Path("src/agent/utils/example_inputs")
EXAMPLE_FILES = sorted(EXAMPLE_INPUTS_DIR.glob("example_input_*.json"))


def load_example(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _get_task_progress(data: dict) -> dict:
    return ((data.get("user") or {}).get("taskProgress") or {})


def _get_submissions(data: dict) -> list:
    return _get_task_progress(data).get("currentPart", {}).get("responseAreas", [])


# ---------------------------------------------------------------------------
# Parametrize over all example files
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[p.name for p in EXAMPLE_FILES])
class TestExampleInputLoading:

    def test_parses_as_valid_chat_request(self, path):
        """JSON can be validated as a ChatRequest without errors."""
        data = load_example(path)
        request = ChatRequest.model_validate(data)
        assert len(request.messages) >= 1

    def test_question_information_fields(self, path):
        """question.title, content, and part count survive the transform."""
        data = load_example(path)
        context = data.get("context", {})
        if not context.get("question"):
            pytest.skip("no question context")

        q_data = context["question"]
        q_info = QuestionDetails(**_build_question_information(context))

        assert q_info.questionTitle == q_data.get("title")
        assert q_info.questionContent == q_data.get("content")
        assert len(q_info.parts) == len(q_data.get("parts", []))

    def test_parts_load_with_correct_ids_and_positions(self, path):
        """Each part's partId and position are preserved after transform."""
        data = load_example(path)
        context = data.get("context", {})
        if not context.get("question"):
            pytest.skip("no question context")

        q_info = QuestionDetails(**_build_question_information(context))
        for part_obj, part_raw in zip(q_info.parts, context["question"].get("parts", [])):
            assert part_obj.publishedPartId == part_raw["partId"], \
                f"partId mismatch: {part_obj.publishedPartId} != {part_raw['partId']}"
            assert part_obj.publishedPartPosition == part_raw["position"], \
                f"position mismatch for part {part_raw['partId']}"

    def test_response_areas_load_with_correct_ids_and_answers(self, path):
        """Each responseArea's id, position, and answer are preserved after transform."""
        data = load_example(path)
        context = data.get("context", {})
        if not context.get("question"):
            pytest.skip("no question context")

        q_info = QuestionDetails(**_build_question_information(context))
        for part_obj, part_raw in zip(q_info.parts, context["question"]["parts"]):
            for ra_obj, ra_raw in zip(part_obj.publishedResponseAreas, part_raw.get("responseAreas", [])):
                expected_id = ra_raw["responseAreaId"]
                assert ra_obj.universalResponseAreaId == expected_id, \
                    f"responseAreaId mismatch in part {part_raw['partId']}: got {ra_obj.universalResponseAreaId}"
                assert ra_obj.position == ra_raw["position"], \
                    f"responseArea position mismatch for {expected_id}"
                assert ra_obj.answer == ra_raw["answer"], \
                    f"answer mismatch for {expected_id}"

    def test_submission_summary_fields(self, path):
        """Submission responseAreaId, counts, and latestSubmission feedback survive the transform."""
        submissions_raw = _get_submissions(load_example(path))
        if not submissions_raw:
            pytest.skip("no submissions in this example")

        summaries = [StudentWorkResponseArea(**s) for s in _build_submission_summary(submissions_raw)]
        for summary, s_raw in zip(summaries, submissions_raw):
            expected_id = s_raw["responseAreaId"]
            assert summary.publishedResponseAreaId == expected_id, \
                f"responseAreaId mismatch: got {summary.publishedResponseAreaId}"
            assert summary.totalSubmissions == s_raw["totalSubmissions"], \
                f"totalSubmissions mismatch for {expected_id}"
            assert summary.totalWrongSubmissions == s_raw["wrongSubmissions"], \
                f"wrongSubmissions mismatch for {expected_id}"

            ls_raw = s_raw.get("latestSubmission")
            if ls_raw:
                assert summary.latestSubmission is not None
                assert summary.latestSubmission.feedback == ls_raw.get("feedback")
                assert summary.latestSubmission.answer == ls_raw.get("answer")
            else:
                assert summary.latestSubmission is None

    def test_access_information_fields(self, path):
        """taskProgress fields (timeTaken, accessStatus, currentPart id/position) are preserved."""
        data = load_example(path)
        task_progress = _get_task_progress(data)
        if not task_progress:
            pytest.skip("no taskProgress in this example")

        access_info = QuestionAccessInformation(**_build_access_information(task_progress))
        current_part_raw = task_progress.get("currentPart", {})

        assert access_info.timeTaken == task_progress.get("timeSpentOnQuestion")
        assert access_info.accessStatus == task_progress.get("accessStatus")
        assert access_info.currentPart.id == current_part_raw.get("partId")
        assert access_info.currentPart.position == current_part_raw.get("position")
        assert access_info.currentPart.timeTakenPart == current_part_raw.get("timeSpentOnPart")

    def test_prompt_is_generated_and_contains_question_title(self, path):
        """Full pipeline produces a non-empty prompt that includes the question title."""
        data = load_example(path)
        context = data.get("context", {})
        if not context.get("question"):
            pytest.skip("no question context")

        task_progress = _get_task_progress(data)
        current_part_progress = task_progress.get("currentPart", {})

        question_information = QuestionDetails(**_build_question_information(context))
        question_submission_summary = [
            StudentWorkResponseArea(**s)
            for s in _build_submission_summary(current_part_progress.get("responseAreas", []))
        ]
        question_access_information = (
            QuestionAccessInformation(**_build_access_information(task_progress))
            if task_progress else None
        )

        prompt = parse_json_to_prompt(
            question_submission_summary,
            question_information,
            question_access_information,
        )

        assert isinstance(prompt, str) and len(prompt) > 0
        title = context["question"].get("title", "")
        if title:
            assert title in prompt, f"Question title '{title}' not found in prompt"
