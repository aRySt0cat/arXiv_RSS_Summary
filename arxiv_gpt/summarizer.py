import asyncio
import json
from pathlib import Path

import yaml
from openai import AsyncOpenAI, OpenAI

from arxiv_gpt.prompts import PROMPT, TOOL_PROMPT
from arxiv_gpt.utils import TITLE_PATTERN, dict_to_tools, find_category, format_summary


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


class ArxivSummarizer:
    def __init__(
        self,
        config: dict,
        description: str,
        model: str = "gpt-3.5-turbo",
        n_parallel: int = 3,
    ):
        self.category_dict = {
            k: [x.lower() for x in v] for k, v in config["category"].items()
        }
        self.summary_items = config["items"]
        self.summary_items["title"] = "論文のタイトル (和訳)"
        self.description = description
        self.tools, self.tool_choice = dict_to_tools(
            self.summary_items, self.description
        )
        self.client = AsyncOpenAI()
        self.n_parallel = n_parallel
        self.model = model

    def filter_entries(self, entries: list[dict]) -> tuple[list[dict], list[str]]:
        filtered_entries = []
        categories = []
        for entry in entries:
            title, _, _, updated = TITLE_PATTERN.match(entry.title).groups()
            category = find_category(title, self.category_dict)
            if category is None or updated == "UPDATED":
                continue
            filtered_entries.append(entry)
            categories.append(category)
        return filtered_entries, categories

    async def acreate_summary(
        self,
        paper: str,
    ) -> dict["str", "str"]:
        item_text = "\n".join(
            f"- {key}: {value}" for key, value in self.summary_items.items()
        )
        prompt = PROMPT.format(paper=paper, summary_items=item_text)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.0,
            max_tokens=3000,
        )
        message = response.choices[0].message
        prompt = TOOL_PROMPT.format(text=message.content)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.0,
            max_tokens=3000,
            tools=self.tools,
            tool_choice=self.tool_choice,
        )
        message = response.choices[0].message
        arguments = json.loads(message.tool_calls[0].function.arguments)
        return arguments

    async def batch_create_summary(self, entries: list[dict], categories) -> list[str]:
        task = []
        for entry in entries:
            title, _, _, _ = TITLE_PATTERN.match(entry.title).groups()
            paper_text = f"Title: {title}\n\n{entry.summary}"
            task.append(self.acreate_summary(paper_text))
        summaries = await asyncio.gather(*task)
        html_texts = [
            format_summary(entry, summary, category)
            for entry, summary, category in zip(entries, summaries, categories)
        ]
        return html_texts
