import time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from lf_toolkit.chat import ChatRequest, ChatResponse, Message
from lf_toolkit.shared.mued_api_v0_1_0 import Role

from src.agent.utils.parse_json_context_to_prompt import (
    parse_json_to_prompt,
    QuestionDetails,
    StudentWorkResponseArea,
    QuestionAccessInformation,
)
from src.agent.agent import invoke_base_agent


def chat_module(request: ChatRequest) -> ChatResponse:
    # EXTRACT FIELDS FROM MUED REQUEST
    conversation_id = request.conversationId
    if conversation_id is None:
        raise Exception("Internal Error: The conversation id is required in the request.")

    context = request.context or {}
    task_progress = (request.user.taskProgress or {}) if request.user else {}
    current_part_progress = task_progress.get("currentPart", {}) if task_progress else {}

    summary = context.get("summary", "") or ""

    conversationalStyle = ""
    if request.user and request.user.preference:
        pref = request.user.preference.model_dump()
        conversationalStyle = pref.get("conversationalStyle", "") or ""

    # All messages except the last are history; last is the current message
    conversation_history = _to_langchain_messages(request.messages[:-1])
    message = request.messages[-1].content

    # Transform mued context/taskProgress into old parse_json_to_prompt format
    question_information = QuestionDetails(**_build_question_information(context)) if context.get("question") else None
    question_submission_summary = [StudentWorkResponseArea(**s) for s in _build_submission_summary(current_part_progress.get("responseAreas", []))]
    question_access_information = QuestionAccessInformation(**_build_access_information(task_progress)) if task_progress else None

    # PARSE QUESTION CONTEXT TO PROMPT
    try:
        question_response_details_prompt = parse_json_to_prompt(
            question_submission_summary,
            question_information,
            question_access_information,
        )
    except Exception as e:
        print("ERROR:: ", e)
        raise Exception("Internal Error: The question response details could not be parsed.")

    # RUN THE AGENT AND MEASURE PROCESSING TIME
    start_time = time.time()
    chatbot_response = invoke_base_agent(
        query=message,
        conversation_history=conversation_history,
        summary=summary,
        conversationalStyle=conversationalStyle,
        question_response_details=question_response_details_prompt,
        session_id=conversation_id,
    )
    end_time = time.time()

    return ChatResponse(
        output=Message(role=Role.ASSISTANT, content=chatbot_response["output"]),
        metadata={
            "summary": chatbot_response["intermediate_steps"][0],
            "conversationalStyle": chatbot_response["intermediate_steps"][1],
            "processingTimeMs": round((end_time - start_time) * 1000),
        },
    )


def _to_langchain_messages(messages):
    result = []
    for m in messages:
        role = str(m.role).upper()
        if role == "USER":
            result.append(HumanMessage(content=m.content))
        elif role == "ASSISTANT":
            result.append(AIMessage(content=m.content))
        elif role == "SYSTEM":
            result.append(SystemMessage(content=m.content))
    return result


def _build_question_information(context: dict) -> dict:
    set_data = context.get("set", {})
    question_data = context.get("question", {})
    return {
        "setNumber": set_data.get("number"),
        "setName": set_data.get("title"),
        "setDescription": set_data.get("description"),
        "questionNumber": question_data.get("number"),
        "questionTitle": question_data.get("title"),
        "questionGuidance": question_data.get("guidance"),
        "questionContent": question_data.get("content"),
        "durationLowerBound": None,
        "durationUpperBound": None,
        "parts": [
            _transform_part(p, i) for i, p in enumerate(question_data.get("parts", []), 1)
        ],
    }


def _transform_part(p: dict, position: int) -> dict:
    return {
        "publishedPartId": p.get("partId"),
        "publishedPartPosition": p.get("position", position),
        "publishedPartContent": p.get("content"),
        "publishedPartAnswerContent": p.get("answerContent"),
        "publishedWorkedSolutionSections": p.get("workedSolutionSections", []),
        "publishedStructuredTutorialSections": p.get("structuredTutorialSections", []),
        "publishedResponseAreas": [
            _transform_response_area(ra, j)
            for j, ra in enumerate(p.get("responseAreas", []), 1)
        ],
    }


def _transform_response_area(ra: dict, position: int) -> dict:
    ra_id = ra.get("responseAreaId")
    return {
        "id": ra_id,
        "position": ra.get("position", position),
        "universalResponseAreaId": ra_id,
        "preResponseText": ra.get("preResponseText"),
        "responseType": ra.get("responseType"),
        "answer": ra.get("answer"),
    }


def _build_submission_summary(submissions: list) -> list:
    return [
        {
            "publishedPartId": None,
            "publishedPartPosition": None,
            "publishedResponseAreaId": s.get("responseAreaId"),
            "publishedResponseAreaPosition": None,
            "responseAreaUniversalId": s.get("responseAreaId"),
            "publishedResponseAreaPreResponseText": None,
            "publishedResponseType": s.get("responseType"),
            "publishedResponseConfig": None,
            "totalSubmissions": s.get("totalSubmissions"),
            "totalWrongSubmissions": s.get("wrongSubmissions"),
            "latestSubmission": s.get("latestSubmission"),
        }
        for s in submissions
    ]


def _build_access_information(task_progress: dict) -> dict:
    current_part = task_progress.get("currentPart", {})
    return {
        "estimatedMinimumTime": None,
        "estimaredMaximumTime": None,
        "timeTaken": task_progress.get("timeSpentOnQuestion"),
        "accessStatus": task_progress.get("accessStatus"),
        "markedDone": task_progress.get("markedDone"),
        "currentPart": {
            "id": current_part.get("partId"),
            "position": current_part.get("position"),
            "universalPartId": current_part.get("partId"),
            "timeTakenPart": current_part.get("timeSpentOnPart"),
            "markedDonePart": current_part.get("markedDone"),
        },
    }
