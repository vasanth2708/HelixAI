import logging
import re
import boto3
from config import Config
from utils.memory import retrieve_context 

logger = logging.getLogger(__name__)
client = boto3.client("bedrock-runtime", region_name=Config.AWS_REGION)

def clean_conversation_text(conversation_history: list) -> str:

    cleaned_lines = []
    for m in conversation_history:
        text = m.get("text", "")
        text = re.sub(r"type:.*", "", text)
        cleaned_lines.append(f"{m['sender']}: {text.strip()}")
    return "\n".join(cleaned_lines)

def question_agents(conversation_history: list, collected_data: dict, session_id: str = None) -> str:
    
    conversation_text = clean_conversation_text(conversation_history)
    
    if session_id:
        last_query = conversation_history[-1]["text"]
        retrieved = retrieve_context(session_id, last_query, k=3)
        if retrieved:
            conversation_text += "\nRetrieved Context:\n" + retrieved

    prompt_text = f"""
            You are Helix, a fictional SellScale HR Agent specialized in recruiting outreach and HR-related tasks.

            Your task is to determine the user's intent from the conversation provided. Return EXACTLY one of the following tokens:
                "DONE", "ADD_STEP", or "EDIT_STEP"
            If the context is ambiguous, you may ask up to 2 brief follow-up questions. Do not output any additional text.

            STRICT RULES:
            1. If the user requests to create or generate new outreach content (e.g., a sales sequence, email draft, or job description), return "DONE".
            2. If the user wants to add a new step to an existing sequence, return "ADD_STEP".
            3. If the user wants to edit an existing step, return "EDIT_STEP".
            4. If the conversation includes the keywords "follow up email" and "interview", return "DONE" immediately without any follow-up questions.
            5. Do not include any extra text, explanations, or confirmation phrases.

            Few-shot examples:
            Example 1:
            User: "Write a sales sequence targeting homeowners in LA Cali."
            Helix: "DONE"

            Example 2:
            User: "Add a step about following up next week."
            Helix: "ADD_STEP"

            Example 3:
            User: "Edit step 2 to mention advanced Python usage."
            Helix: "EDIT_STEP"

            Example 4:
            User: "Write an email draft for interview follow-up."
            Helix: "DONE"

            Conversation so far:
            {conversation_text}
            """.strip()


    
    try:
        response = client.converse(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt_text}]}]
        )
        llm_reply = response["output"]["message"]["content"][0]["text"].strip()
        logger.info(f"Question Agent reply: {llm_reply}")
        return llm_reply
    except Exception as e:
        logger.error(f"Question Agent LLM call failed: {e}")
        return "Could you clarify your request?"
