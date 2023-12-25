import re

TITLE_PATTERN = re.compile(r"(.*) \(arXiv:(\d+.\d+v\d) \[(.*)\]\s*(.*)\)")

ITEM_FORMAT = """\
<h3>{heading}</h3>
<div>{content}</div>
"""


def find_category(text: str, category_dict: dict[str, list[str]]) -> str | None:
    text_lower = text.lower()
    for category, keywords in category_dict.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return None


def format_authors(authors: list[dict[str, str]]) -> str:
    names = authors[0].name.split(", ")
    if len(names) > 3:
        names = names[:2] + ["...", names[-1]]
    author_text = ", ".join(names)
    return author_text


def format_summary(entry: dict, summary: dict[str, str], category: str) -> str:
    title_en, idx, arxiv_category, updated = TITLE_PATTERN.match(entry.title).groups()
    text = f"<h2>{summary['title']} [{category}]</h2>"
    text += f'<h3><a href="{entry.link}">{title_en}</a></h3>'
    text += format_authors(entry.authors) + "<br>"
    summary.pop("title")
    for key, value in summary.items():
        text += ITEM_FORMAT.format(heading=key, content=value)
    return text


def dict_to_tools(
    summary_items: dict[str, str], summary_style: str
) -> tuple[list[dict], dict]:
    args = {
        key: {"type": "string", "description": value}
        for key, value in summary_items.items()
    }

    func = {
        "name": "summarize",
        "description": summary_style,
        "parameters": {
            "type": "object",
            "properties": {
                **args,
            },
            "required": list(args.keys()),
        },
    }

    tools = [{"type": "function", "function": func}]
    tool_choice = {"type": "function", "function": {"name": func["name"]}}
    return tools, tool_choice
