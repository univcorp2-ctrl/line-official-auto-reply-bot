# 初期設定ガイド

## 目的

LINE公式アカウントに届いたメッセージを、このBotで自動返信できる状態にします。

## 先に確認すること

初めて設定する場合は、先に `docs/preparation.md` を確認してください。このページでは、事前準備が終わった状態から、Botを起動してLINEにWebhook URLを登録するところまで説明します。

事前準備で必要なもの:

```text
LINE公式アカウント
Messaging APIチャネル
Channel Secret
Channel Access Token
HTTPS公開URL
```

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

最初はルール返信だけで動かすのがおすすめです。

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

## ローカルで動作確認する場合

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

ヘルスチェック:

```bash
curl http://localhost:8000/healthz
```

LINEから直接ローカルPCには到達できないため、ngrokやCloudflare TunnelなどでHTTPS公開URLを作ってWebhook URLに設定します。

## Dockerで起動

```bash
cp .env.example .env
docker compose up --build
```

## デプロイ後に確認するURL

デプロイ後、まず次のURLにアクセスしてBotが起動していることを確認します。

```text
https://your-public-domain.example.com/healthz
```

次に、LINE Developers ConsoleにWebhook URLとして次を登録します。

```text
https://your-public-domain.example.com/webhook
```

## Webhook URL設定

デプロイ後、次の形式のURLをLINE Developers Consoleに設定します。

```text
https://your-public-domain.example.com/webhook
```

その後、Webhook利用を有効化し、Verifyを実行します。Verify時は `events: []` のWebhookが送られることがあるため、アプリは署名検証に成功すれば `200 OK` を返します。

Webhook redeliveryを使う場合は、LINE Developers ConsoleのMessaging API設定で有効化してください。

## 動作テスト

LINE公式アカウントを友だち追加して、次のメッセージを送ってください。

```text
営業時間を教えて
予約したい
料金を知りたい
担当者に代わって
```

期待する返信は `app/rules.yml` に定義されています。

## ルール返信の変更

`app/rules.yml` を編集します。

```yaml
keywords:
  - contains: 営業時間
    reply: "営業時間は平日10:00〜18:00です。"
```

変更後、アプリを再起動してください。

## AI返信を有効化する流れ

最初からAI返信にすると、意図しない返信文になる可能性があります。まずはルール返信だけでLINE接続を確認し、その後にAI返信を有効化してください。

1. `REPLY_MODE=rules` でWebhook疎通確認
2. `app/rules.yml` の定型返信を調整
3. `OPENAI_API_KEY` を本番環境のSecretに登録
4. `REPLY_MODE=hybrid` に変更
5. キーワードに該当しない問い合わせだけAI返信されるか確認

## 本番の注意点

- SecretはGitHubにコミットしないでください。
- `.env` は `.gitignore` 済みです。
- Webhook URLはHTTPS必須です。
- 署名検証に失敗する場合、Channel Secretが違う、本文が途中で改変されている、プロキシがbodyを変更している可能性があります。
- Reply Tokenは短時間かつ一度だけ使える前提で、Webhook受信時にすぐ返信します。
- LINE公式アカウント側の標準応答とBot返信が二重にならないよう設定を確認してください。
- メッセージ配信数や料金プランを確認してください。
- クレーム、解約、個人情報、予約変更などは人が確認する運用を用意してください。

## 障害対応

1. `/healthz` が200を返すか確認
2. LINE Developers ConsoleのWebhookエラー統計を確認
3. アプリログで `invalid line signature` を確認
4. Channel SecretとAccess Tokenを再確認
5. Reply APIのHTTPステータスと `x-line-request-id` を確認
6. `DRY_RUN=true` のままになっていないか確認
7. LINE公式アカウント側のWebhook利用設定を確認
