import json

from openai import OpenAI

from arxiv_gpt.prompts import PROMPT, TOOL_PROMPT


def create_summary(
    summary_items: dict[str, str],
    paper: str,
    tools: list[dict],
    tool_choice: dict,
    client: OpenAI,
    model="gpt-3.5-turbo",
) -> dict["str", "str"]:
    item_text = "\n".join(f"- {key}: {value}" for key, value in summary_items.items())
    prompt = PROMPT.format(paper=paper, summary_items=item_text)
    message = (
        client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.0,
            max_tokens=3000,
        )
        .choices[0]
        .message
    )
    prompt = TOOL_PROMPT.format(text=message.content)
    message = (
        client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.0,
            max_tokens=3000,
            tools=tools,
            tool_choice=tool_choice,
        )
        .choices[0]
        .message
    )
    arguments = json.loads(message.tool_calls[0].function.arguments)
    return arguments
