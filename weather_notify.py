import os
import requests
from datetime import datetime, timezone, timedelta

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
LATITUDE      = float(os.environ.get("LATITUDE",  "35.6074"))
LONGITUDE     = float(os.environ.get("LONGITUDE", "140.1065"))
LOCATION_NAME = os.environ.get("LOCATION_NAME", "幕張本郷（千葉市花見川区）")

JST = timezone(timedelta(hours=9))

WEATHER_CODES = {
    0:  ("快晴",          "☀️"),
    1:  ("ほぼ晴れ",      "🌤️"),
    2:  ("部分的に曇り",  "⛅"),
    3:  ("曇り",          "☁️"),
    45: ("霧",            "🌫️"),
    48: ("霧氷",          "🌫️"),
    51: ("霧雨（弱）",    "🌦️"),
    53: ("霧雨",          "🌦️"),
    55: ("霧雨（強）",    "🌧️"),
    61: ("小雨",          "🌧️"),
    63: ("雨",            "🌧️"),
    65: ("大雨",          "🌧️"),
    71: ("小雪",          "🌨️"),
    73: ("雪",            "❄️"),
    75: ("大雪",          "❄️"),
    80: ("にわか雨",      "🌦️"),
    81: ("にわか雨（中）","🌧️"),
    82: ("にわか雨（強）","⛈️"),
    95: ("雷雨",          "⛈️"),
    96: ("雷雨+ひょう",   "⛈️"),
    99: ("雷雨+大ひょう", "⛈️"),
}

WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]
ROKKI       = ["大安", "赤口", "先勝", "友引", "先負", "仏滅"]

# ── 六曜計算（旧暦 (月+日) % 6 アルゴリズム） ──
def _julian_day(year, month, day):
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5

def get_rokki(year, month, day):
    jd = _julian_day(year, month, day)
    days_since = jd - 2415020.5          # 1900-01-01 基点
    lunation   = days_since / 29.530588853
    lunar_month = int(lunation % 12) + 1
    lunar_day   = int((lunation % 1) * 29.530588853) + 1
    return ROKKI[(lunar_month + lunar_day) % 6]
# ────────────────────────────────────────────────

def precip_bar(prob):
    filled = prob // 20
    return "🟦" * filled + "⬜" * (5 - filled)

def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m,precipitation_probability,weathercode",
        "timezone": "Asia/Tokyo",
        "forecast_days": 1,
    }
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    return res.json()

def build_message(data):
    hourly    = data["hourly"]
    times     = hourly["time"]
    temps     = hourly["temperature_2m"]
    prec_prob = hourly["precipitation_probability"]
    codes     = hourly["weathercode"]

    now    = datetime.now(JST)
    wday   = WEEKDAYS_JA[now.weekday()]
    rokki  = get_rokki(now.year, now.month, now.day)
    date_str = now.strftime("%Y年%m月%d日")

    target_hours = {0, 3, 6, 9, 12, 15, 18, 21}
    rows = []
    for i, t in enumerate(times):
        dt = datetime.fromisoformat(t)
        if dt.hour in target_hours:
            desc, emoji = WEATHER_CODES.get(codes[i], ("不明", "❓"))
            prob = prec_prob[i]
            rows.append(
                f"`{dt.strftime('%H:%M')}` {emoji} **{desc}**　"
                f"{temps[i]:.1f}°C　💧{prob:3d}% {precip_bar(prob)}"
            )

    lines = [
        f"## 🌅 {LOCATION_NAME}の天気予報 — {date_str}（{wday}）｜{rokki}",
        "",
        *rows,
        "",
        "─────────────────────────",
        "*データ提供: [Open-Meteo](https://open-meteo.com/) | 3時間ごと全時間帯*",
    ]
    return "\n".join(lines)

def send_to_discord(message):
    res = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message},
        timeout=10,
    )
    res.raise_for_status()
    print("✅ 送信成功")

if __name__ == "__main__":
    data = get_weather()
    msg  = build_message(data)
    print(msg)
    send_to_discord(msg)
```

---

### 出力イメージ
```
## 🌅 幕張本郷（千葉市花見川区）の天気予報 — 2026年03月21日（土）｜先勝

`00:00` ☀️ **快晴**　6.0°C　💧  0% ⬜⬜⬜⬜⬜
`03:00` ☀️ **快晴**　5.0°C　💧  0% ⬜⬜⬜⬜⬜
`06:00` ⛅ **部分的に曇り**　4.0°C　💧  0% ⬜⬜⬜⬜⬜
`09:00` ⛅ **部分的に曇り**　6.0°C　💧  0% ⬜⬜⬜⬜⬜
`12:00` ☁️ **曇り**　9.0°C　💧  0% ⬜⬜⬜⬜⬜
`15:00` ☀️ **快晴**　10.0°C　💧  0% ⬜⬜⬜⬜⬜
`18:00` 🌦️ **にわか雨**　8.0°C　💧 81% 🟦🟦🟦🟦⬜
`21:00` ☁️ **曇り**　8.0°C　💧  0% ⬜⬜⬜⬜⬜

─────────────────────────
*データ提供: Open-Meteo | 3時間ごと全時間帯*
