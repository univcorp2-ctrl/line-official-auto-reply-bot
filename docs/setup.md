# 初期設定ガイド

## 目的

LINE公式アカウントに届いたメッセージを、このBotで自動返信できる状態にします。

## 必要なもの

- LINE公式アカウント
- LINE Developers Consoleにアクセスできる権限
- HTTPSで公開できるサーバー、Render、Fly.io、Cloud Run、Railwayなど
- 任意: OpenAI API key

## LINE側で取得する値

### `LINE_CHANNEL_SECRET`

LINE Developers Consoleで対象のMessaging APIチャネルを開き、Basic settingsのChannel secretを確認します。

### `LINE_CHANNEL_ACCESS_TOKEN`

同じチャネルのMessaging API設定で、Channel access tokenを発行します。この値はLINE Reply APIを呼ぶために使います。

## アプリ側の環境変数

```env
LINE_CHANNEL_SECRET=取得したChannel secret
LINE_CHANNEL_ACCESS_TOKEN=取得したChannel access token
DRY_RUN=false
REPLY_MODE=rules
DATABASE_URL=sqlite:///./data/line_events.db
```

AI返信も使う場合:

```env
REPLY_MODE=hybrid
OPENAI_API_KEY=OpenAIのAPI key
OPENAI_MODEL=gpt-5.5
```

## Webhook URL設定

デプロイ後、次の形式のURLをLINE Developers Consoleに設定します。

```text
https://your-public-domain.example.com/webhook
```

その後、Webhook利用を有効化し、Verifyを実行します。Verify時は `events: []` のWebhookが送られるため、アプリは署名検証に成功すれば `200 OK` を返します。

## ローカルで動作確認する場合

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

LINEから直接ローカルPCには到達できないため、ngrokやCloudflare TunnelなどでHTTPS公開URLを作ってWebhook URLに設定します。

## Dockerで起動

```bash
cp .env.example .env
docker compose up --build
```

## ルール返信の変更

`app/rules.yml` を編集します。

```yaml
keywords:
  - contains: 営業時間
    reply: "営業時間は平日10:00〜18:00です。"
```

変更後、アプリを再起動してください。

## 本番の注意点

- SecretはGitHubにコミットしないでください。
- `.env` は `.gitignore` 済みです。
- Webhook URLはHTTPS必須です。
- 署名検証に失敗する場合、Channel Secretが違う、本文が途中で改変されている、プロキシがbodyを変更している可能性があります。
- Reply Tokenは短時間かつ一度だけ使える前提で、Webhook受信時にすぐ返信します。
- LINE公式アカウント側の標準応答とBot返信が二重にならないよう設定を確認してください。
- メッセージ配信数や料金プランを確認してください。

## 障害対応

1. `/healthz` が200を返すか確認
2. LINE Developers ConsoleのWebhookエラー統計を確認
3. アプリログで `invalid line signature` を確認
4. Channel SecretとAccess Tokenを再確認
5. Reply APIのHTTPステータスと `x-line-request-id` を確認
