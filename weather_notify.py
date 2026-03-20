# -*- coding: utf-8 -*-
import os
import requests
from datetime import datetime, timezone, timedelta

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
DISCORD_BOT_TOKEN   = os.environ["DISCORD_BOT_TOKEN"].strip()
DISCORD_CHANNEL_ID  = os.environ["DISCORD_CHANNEL_ID"]

LATITUDE      = float(os.environ.get("LATITUDE",  "35.6374"))
LONGITUDE     = float(os.environ.get("LONGITUDE", "140.0641"))
LOCATION_NAME = os.environ.get("LOCATION_NAME", "\u5e55\u5f35\u672c\u90f7\uff08\u5343\u8449\u5e02\u82b1\u898b\u5ddd\u533a\uff09")

JST = timezone(timedelta(hours=9))

WEATHER_CODES = {
    0:  ("\u5feb\u6674",           "\u2600\ufe0f"),
    1:  ("\u307b\u307c\u6674\u308c",       "\U0001f324\ufe0f"),
    2:  ("\u90e8\u5206\u7684\u306b\u66c7\u308a",   "\u26c5"),
    3:  ("\u66c7\u308a",           "\u2601\ufe0f"),
    45: ("\u971e",             "\U0001f32b\ufe0f"),
    48: ("\u971e\u6c37",           "\U0001f32b\ufe0f"),
    51: ("\u971e\u96e8\uff08\u5f31\uff09",     "\U0001f326\ufe0f"),
    53: ("\u971e\u96e8",           "\U0001f326\ufe0f"),
    55: ("\u971e\u96e8\uff08\u5f37\uff09",     "\U0001f327\ufe0f"),
    61: ("\u5c0f\u96e8",           "\U0001f327\ufe0f"),
    63: ("\u96e8",             "\U0001f327\ufe0f"),
    65: ("\u5927\u96e8",           "\U0001f327\ufe0f"),
    71: ("\u5c0f\u96ea",           "\U0001f328\ufe0f"),
    73: ("\u96ea",             "\u2744\ufe0f"),
    75: ("\u5927\u96ea",           "\u2744\ufe0f"),
    80: ("\u306b\u308f\u304b\u96e8",       "\U0001f326\ufe0f"),
    81: ("\u306b\u308f\u304b\u96e8\uff08\u4e2d\uff09", "\U0001f327\ufe0f"),
    82: ("\u306b\u308f\u304b\u96e8\uff08\u5f37\uff09", "\u26c8\ufe0f"),
    95: ("\u96f7\u96e8",           "\u26c8\ufe0f"),
    96: ("\u96f7\u96e8+\u3072\u3087\u3046",    "\u26c8\ufe0f"),
    99: ("\u96f7\u96e8+\u5927\u3072\u3087\u3046",  "\u26c8\ufe0f"),
}

WEEKDAYS_JA = ["\u6708", "\u706b", "\u6c34", "\u6728", "\u91d1", "\u571f", "\u65e5"]
ROKKI       = ["\u5927\u5b89", "\u8d64\u53e3", "\u5148\u52dd", "\u53cb\u5f15", "\u5148\u8ca0", "\u4ecf\u6ec5"]

def _julian_day(year, month, day):
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5

def get_rokki(year, month, day):
    jd = _julian_day(year, month, day)
    days_since  = jd - 2415020.5
    lunation    = days_since / 29.530588853
    lunar_month = int(lunation % 12) + 1
    lunar_day   = int((lunation % 1) * 29.530588853) + 1
    return ROKKI[(lunar_month + lunar_day) % 6]

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

    now      = datetime.now(JST)
    wday     = WEEKDAYS_JA[now.weekday()]
    rokki    = get_rokki(now.year, now.month, now.day)
    date_str = now.strftime("%Y\u5e74%m\u6708%d\u65e5")

    target_hours = {0, 3, 6, 9, 12, 15, 18, 21}
    rows = []
    for i, t in enumerate(times):
        dt = datetime.fromisoformat(t)
        if dt.hour in target_hours:
            desc, emoji = WEATHER_CODES.get(codes[i], ("\u4e0d\u660e", "?"))
            prob = prec_prob[i]
            rows.append(
                f"`{dt.strftime('%H:%M')}` {emoji} **{desc}**\u3000"
                f"{temps[i]:.1f}\u00b0C\u3000\U0001f4a7{prob:3d}%"
            )

    lines = [
        f"## \U0001f305 {LOCATION_NAME}\u306e\u5929\u6c17\u4e88\u5831 \u2014 {date_str}\uff08{wday}\uff09\uff5c{rokki}",
        "",
        *rows,
        "",
        "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500",
        "*\u30c7\u30fc\u30bf\u63d0\u4f9b: [Open-Meteo](https://open-meteo.com/) | 3\u6642\u9593\u3054\u3068\u5168\u6642\u9593\u5e2f*",
    ]
    return "\n".join(lines)

def send_and_pin(message):
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}

    # 1. メッセージ送信
    res = requests.post(
        f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages",
        headers=headers,
        json={"content": message},
        timeout=10,
    )
    res.raise_for_status()
    message_id = res.json()["id"]
    print(f"\u2705 \u30e1\u30c3\u30bb\u30fc\u30b8\u9001\u4fe1\u6210\u529f: {message_id}")

    # 2. 古いピン留めを全部外す
    pins = requests.get(
        f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/pins",
        headers=headers,
        timeout=10,
    ).json()
    for pin in pins:
        requests.delete(
            f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/pins/{pin['id']}",
            headers=headers,
            timeout=10,
        )
    print(f"\u2705 \u53e4\u3044\u30d4\u30f3\u7559\u3081\u3092{len(pins)}\u4ef6\u89e3\u9664")

    # 3. 新しいメッセージをピン留め
    requests.put(
        f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/pins/{message_id}",
        headers=headers,
        timeout=10,
    ).raise_for_status()
    print("\u2705 \u30d4\u30f3\u7559\u3081\u6210\u529f")

if __name__ == "__main__":
    data = get_weather()
    msg  = build_message(data)
    print(msg)
    send_and_pin(msg)
