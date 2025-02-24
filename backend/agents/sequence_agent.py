import json
import logging
import re
import boto3

logger = logging.getLogger(__name__)

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-west-2")

def generate_new_sequence(collected_data: dict) -> dict:

    summary_text = "\n".join([f"{k}: {v}" for k, v in collected_data.items()])
    
    prompt = f"""
                You are Helix, an AI recruiting assistant (prototype for SellScale HR).
                Based on the following data:
                {summary_text}

                SPECIAL RULE:
                If the content is for an interview follow-up email (i.e. the data includes terms like "interview" and "follow up email"),
                generate a single email draft that is split into multiple steps.
                Each step should represent a section of the email (for example: a greeting, an introductory paragraph, the main body, and a closing).
                Do not generate multiple separate emails.

                Otherwise, generate a standard outreach sequence.

                Return the result in valid JSON with the following format:
                {{
                "sequence": [
                    {{ "step": 1, "message": "..." }},
                    {{ "step": 2, "message": "..." }},
                    ... (as many steps as needed)
                ]
                }}

                Return only the JSON object.
                    """.strip()
                    
    return _call_llm_and_extract_sequence(prompt)

def add_additional_step_with_detail(existing_sequence: list, additional_detail: str) -> dict:
    """
    Generate exactly one new step based on the additional detail provided.
    Returns a dict with a "sequence" key containing a list with one new step.
    """
    next_step_num = len(existing_sequence) + 1
    steps_text = "\n".join([f"Step {s['step']}: {s['message']}" for s in existing_sequence])
    
    prompt = f"""
            We have an existing sequence:
            {steps_text}

            Based on the following additional detail:
            {additional_detail}

            Generate exactly one new step that should be appended as step {next_step_num}.
            Return only the new step as a JSON object in the following format:
            {{
            "sequence": [
                {{
                "step": {next_step_num},
                "message": "..."
                }}
            ]
            }}

            Do not include any steps from the existing sequence in your output.
                """.strip()
                
    return _call_llm_and_extract_sequence(prompt)


def _call_llm_and_extract_sequence(prompt_text: str) -> dict:

    try:
        response = bedrock_runtime.converse(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt_text}]}]
        )
        raw_text = response["output"]["message"]["content"][0]["text"]
        logger.info(f"Sequence Agent raw response: {raw_text}")

        try:
            parsed = json.loads(raw_text)
            return parsed
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                extracted = match.group(0)
                parsed = json.loads(extracted)
                return parsed
            else:
                raise Exception("No valid JSON found in LLM response.")
    except Exception as e:
        logger.error(f"Sequence agent call failed: {e}")
        raise Exception("Sequence agent could not generate or update the sequence.") from e

def edit_step_with_llm(existing_sequence: list, user_command: str) -> dict:
    """
    Use the LLM to update the existing sequence based on the user's edit command.
    The user command should specify which step to edit and the new content.
    The LLM should update only that step's message and leave the other steps unchanged.
    
    Returns a dict with a "sequence" key containing the updated full sequence.
    """
    steps_text = "\n".join([f"Step {s['step']}: {s['message']}" for s in existing_sequence])
    prompt = f"""
            We have an existing sequence:
            {steps_text}

            User command: {user_command}

            Please update only the step specified in the user command by changing its message to the new content, and leave all other steps unchanged.
            Return the complete updated sequence in valid JSON format with the following structure:
            {{
                "sequence": [
                {{ "step": 1, "message": "..." }},
                {{ "step": 2, "message": "..." }},
                ...
                ]
            }}
            Do not output any additional text.
                """.strip()
                
    return _call_llm_and_extract_sequence(prompt)
