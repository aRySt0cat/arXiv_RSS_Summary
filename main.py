import asyncio
import os
from datetime import datetime

import feedparser
import yaml
from dotenv import load_dotenv
from tqdm import tqdm

from arxiv_gpt.mail import send_mail
from arxiv_gpt.summarizer import ArxivSummarizer

load_dotenv()


def main():
    config_path = "config.yaml"
    n_parallel = 3
    description = "各項目について引数を与えることで、要約を作成する。"

    # 準備
    with open(config_path) as f:
        config = yaml.safe_load(f)
    summarizer = ArxivSummarizer(config, description, n_parallel=n_parallel)

    login_address = os.environ["LOGIN_ADDRESS"]
    login_password = os.environ["LOGIN_PASSWORD"]
    mailing_list = config["mailing_list"]
    today = datetime.now().strftime("%Y年%m月%d日")
    mail_title = f"SummarXiv :{today}"

    # フィードの取得
    url = "https://export.arxiv.org/rss/" + config["arxiv_category"]
    feed = feedparser.parse(url)

    entries, categories = summarizer.filter_entries(feed.entries)
    pbar = tqdm(total=len(entries))
    contents = []
    for i in range(0, len(entries), n_parallel):
        entry_batch = entries[i : i + n_parallel]
        category_batch = categories[i : i + n_parallel]
        summaries = asyncio.run(
            summarizer.batch_create_summary(entry_batch, category_batch)
        )
        contents += summaries
        pbar.update(len(entry_batch))
    print(f"Summarized {len(entries)} papers out of {len(feed.entries)} papers.")
    pbar.close()
    if len(contents) == 0:
        return
    send_mail(
        mail_title,
        content="<br>\n".join(contents),
        login_address=login_address,
        login_password=login_password,
        address_list=mailing_list,
    )


if __name__ == "__main__":
    main()
