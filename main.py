import os
from datetime import datetime

import feedparser
import yaml
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

from arxiv_gpt.mail import send_mail
from arxiv_gpt.summarizer import create_summary
from arxiv_gpt.utils import TITLE_PATTERN, dict_to_tools, find_category, format_summary

load_dotenv()


def main():
    config_yaml = "config.yaml"

    # 準備
    with open(config_yaml) as f:
        config = yaml.safe_load(f)
    url = "https://export.arxiv.org/rss/" + config["arxiv_category"]
    category_dict = {k: [x.lower() for x in v] for k, v in config["category"].items()}
    summary_items = config["items"]
    summary_items["title"] = "論文のタイトル (和訳)"

    login_address = os.environ["LOGIN_ADDRESS"]
    login_password = os.environ["LOGIN_PASSWORD"]
    mailing_list = config["mailing_list"]
    today = datetime.now().strftime("%Y年%m月%d日")
    mail_title = f"SummarXiv ({today})"

    description = "各項目について引数を与えることで、要約を作成する。"
    tools, tool_choice = dict_to_tools(summary_items, description)
    client = OpenAI()

    # フィードの取得
    feed = feedparser.parse(url)
    pbar = tqdm(total=len(feed.entries))
    count = 0
    contents = []
    for entry in feed.entries:
        pbar.update(1)
        title, idx, arxiv_category, updated = TITLE_PATTERN.match(entry.title).groups()
        # tqdm で title を表示
        pbar.set_description(idx)

        category = find_category(title, category_dict)
        if category is None or updated == "UPDATED":
            continue
        paper_text = f"Title: {title}\n\n{entry.summary}"
        summary = create_summary(
            client=client,
            summary_items=summary_items,
            paper=paper_text,
            tools=tools,
            tool_choice=tool_choice,
        )
        html_text = format_summary(entry, summary, category)
        contents.append(html_text)
        count += 1
    send_mail(
        mail_title,
        content="<br>\n".join(contents),
        login_address=login_address,
        login_password=login_password,
        address_list=mailing_list,
    )
    print(f"Summarized {count} papers out of {len(feed.entries)} papers.")
    pbar.close()


if __name__ == "__main__":
    main()
