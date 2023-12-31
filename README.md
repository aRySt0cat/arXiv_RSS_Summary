# このアプリは何?

arXiv の RSS を取得して、自分の興味のあるカテゴリの論文のみを要約してメールで送信するアプリです。
![スクリーンショット 0005-12-25 23 36 28](https://github.com/aRySt0cat/arXiv_RSS_Summary/assets/55921454/c5e2e5a4-c910-45e9-b814-e7837066e9f7)

# 設定

設定は `config.yaml` と　`.env` に記載します。

## config.yaml
以下の3つのキーを設定してください。
- category: 自作のカテゴリを設定する
- items: 要約に含めたい内容を記載する
- mailing_list: メール送信先を記載する

`category` は、以下のように設定できます。これによって設定されたワードがタイトルに含まれている場合、そのカテゴリとして扱われます。
いずれかのカテゴリに該当する場合、要約がメールで送信されます。
```yaml
カテゴリ名:
    - ワード1
    - ワード2
```

`item` は以下のように設定できます。`item_name` は英語で記載してください。
```yaml
item_name: 要約方法の説明
```

## .env
`.env` では、以下の3つの環境変数を設定します。

- LOGIN_ADDRESS: 送信元になるメールアドレス
- LOGIN_PASSWORD: 送信元になるメールアドレスのアプリパスワード ([後述](#アプリパスワードについて))
- OPENAI_API_KEY: OpenAI API のキー

# 実行方法

`main.py` を実行すると、その日の arXiv の RSS を取得して、カテゴリに設定した論文の要約をメールで送信します。  
定期実行する場合は、`cron` などを利用してください。

# アプリパスワードについて
(Gmail で利用することを想定しています。)  

以下の手順でアプリパスワードを設定してください。
1. [アカウントページ](https://myaccount.google.com/) の左にある「セキュリティ」をクリックし、2段階認証を有効にします。  
2. [https://myaccount.google.com/u/0/apppasswords](https://myaccount.google.com/u/0/apppasswords) にアクセスし、適当な名前を設定します。  
3. パスワードが設定されるため、それを `LOGIN_PASSWORD` に設定してください。
