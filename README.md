# 🌤️ 毎朝天気Discord通知システム（千葉市・全時間帯）

毎日 朝7時（JST）に、当日0時〜21時の天気を3時間ごとにDiscordへ自動送信します。

---

## ✅ セットアップ手順

### STEP 1 — GitHubリポジトリを作成してPush

1. GitHub で新しいリポジトリを作成（例: `weather-discord-bot`）
2. このリポジトリの3ファイルをそのまま配置してPush

### STEP 2 — Discord Webhook URLを取得

1. Discordを開き、通知を送りたいサーバーのチャンネルを右クリック
2. 「チャンネルの編集」→「連携サービス」→「ウェブフック」
3. 「新しいウェブフック」をクリック
4. 名前を設定（例: `天気Bot`）して「ウェブフックURLをコピー」
5. このURLを控えておく（https://discord.com/api/webhooks/... の形式）

### STEP 3 — GitHub Secretsに登録

GitHubリポジトリの **Settings → Secrets and variables → Actions**

#### 「Secrets」タブ
| 名前 | 値 |
|------|-----|
| `DISCORD_WEBHOOK_URL` | コピーしたDiscord Webhook URL |

#### 「Variables」タブ
| 名前 | 値 |
|------|-----|
| `LATITUDE` | `35.6074` |
| `LONGITUDE` | `140.1065` |
| `LOCATION_NAME` | `千葉市` |

### STEP 4 — 動作テスト

GitHubリポジトリの **Actions タブ** → 「毎朝天気通知」→「Run workflow」→「Run workflow」ボタン

Discordに通知が届けば成功です！

---

## 📍 地域を変更したい場合

| 都市 | LATITUDE | LONGITUDE |
|------|----------|-----------|
| 千葉市 | 35.6074 | 140.1065 |
| 東京 | 35.6895 | 139.6917 |
| 大阪 | 34.6937 | 135.5023 |
| 札幌 | 43.0618 | 141.3545 |
| 福岡 | 33.5904 | 130.4017 |

---

## 📋 通知フォーマット例
```
🌅 千葉市の天気予報 — 2026年03月21日（土）

00:00 ☁️ 曇り　12.3°C　💧 20% 🟦⬜⬜⬜⬜
03:00 ☁️ 曇り　11.8°C　💧 15% ⬜⬜⬜⬜⬜
06:00 🌤️ ほぼ晴れ　12.5°C　💧 10% ⬜⬜⬜⬜⬜
09:00 ☀️ 快晴　15.2°C　💧  5% ⬜⬜⬜⬜⬜
12:00 ☀️ 快晴　18.7°C　💧  5% ⬜⬜⬜⬜⬜
15:00 ⛅ 部分的に曇り　17.4°C　💧 20% 🟦⬜⬜⬜⬜
18:00 🌧️ 雨　14.1°C　💧 70% 🟦🟦🟦⬜⬜
21:00 🌧️ 雨　13.0°C　💧 80% 🟦🟦🟦🟦⬜
```

---

## ⚠️ 注意事項

- **APIキー不要**: Open-Meteo は完全無料・登録なしで利用可能
- **cron時刻**: GitHub ActionsのcronはUTC基準のため `0 22 * * *` がJST 07:00に相当
- **スマホの現在地について**: GitHub Actionsはクラウドサーバー上で動くため、スマホのリアルタイム位置情報は取得できません。固定の緯度・経度を設定してください
```

---

## 🚀 完全な手順まとめ
```
1. GitHubに新リポジトリ作成
       ↓
2. 上の3ファイルをコピーしてPush
       ↓
3. Discord: チャンネル編集 → 連携サービス → Webhook作成 → URLコピー
       ↓
4. GitHub: Settings → Secrets → DISCORD_WEBHOOK_URL を登録
   GitHub: Settings → Variables → LATITUDE / LONGITUDE / LOCATION_NAME を登録
       ↓
5. Actions → Run workflow でテスト実行
       ↓
6. 毎朝7時に自動で届く 🎉
