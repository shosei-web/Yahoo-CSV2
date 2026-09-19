import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ==========================================
# 0. 設定（DiscordのWebhook URL）
# ==========================================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1545772650364797019/pGOCZzmtDhy-gifnFXitn9Ao8nRyprOP8m2l7M0omRoNwPVXAWYGYXc1OM7OOzCqii_3"


# --- 外部関数：Discordへメッセージを送る処理 ---
def send_discord_notification(message):
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print(" -> Discordへの通知に成功しました！")
    else:
        print(f" -> 通知失敗: {response.status_code}")


# ==========================================
# 1. Yahoo!ニュースのトップページから一覧を取得
# ==========================================
url = "https://news.yahoo.co.jp/"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
response = requests.get(url, headers=headers)
response.encoding = response.apparent_encoding

soup = BeautifulSoup(response.text, "html.parser")
articles_list = []

for link in soup.find_all("a"):
    href = link.get("href", "")
    title = link.text.strip()

    if "/pickup/" in href or ("news.yahoo.co.jp/articles/" in href):
        if title and len(title) > 5:
            articles_list.append({"title": title, "url": href})

# 最新3件だけに制限（テスト用）
articles_list = articles_list[:3]

# ==========================================
# 2. 本文取得 ＆ CSV用データの蓄積 ＆ Discord通知（2段階目）
# ==========================================
news_data = []

print(f"全 {len(articles_list)} 件の処理を開始します...")

for article in articles_list:
    target_url = article["url"]
    title = article["title"]

    time.sleep(1)

    try:
        res = requests.get(target_url, headers=headers)
        res.encoding = res.apparent_encoding
        article_soup = BeautifulSoup(res.text, "html.parser")

        # 本文が入っている段落（<p>タグ）を集めて結合
        paragraphs = article_soup.find_all("p")
        body_text = "\n".join(
            [p.text.strip() for p in paragraphs if len(p.text.strip()) > 0]
        )

        # ①【CSV保存用】リストにデータを追加（本文全文を入れる）
        news_data.append(
            {"title": title, "url": target_url, "body": body_text}
        )
        print(f"取得成功: {title[:15]}...")

        # ②【Discord通知用】メッセージを作成して送信する 🌟（ここを追加！）
        # 本文の先頭100文字だけを抜き出して通知用にする
        summary = body_text[:100].replace("\n", " ") + "..."

        notification_text = (
            f"📢 **【最新ニュース通知】**\n"
            f"**タイトル:** {title}\n"
            f"**概要:** {summary}\n"
            f"**URL:** {target_url}"
        )

        # 関数を呼び出してDiscordに送信！
        send_discord_notification(notification_text)

    except Exception as e:
        print(f"取得失敗 ({title[:15]}...): {e}")

# ==========================================
# 3. pandasでCSVに保存
# ==========================================
df = pd.DataFrame(news_data)
df.to_csv("news_with_body.csv", index=False, encoding="utf-8-sig")
print("\n完了！ news_with_body.csv に保存し、Discordへの通知も完了しました。")