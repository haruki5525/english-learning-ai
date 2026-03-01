import datetime
from notion_client import Client
from groq import Groq

# 設定
GROQ_KEY = "YOUR_GROQ_KEY"
NOTION_TOKEN = "YOUR_NOTION_KEY"
DATABASE_ID = "31688e0072468027b150e7fa2512e01b"

# クライアント設定
groq_client = Groq(api_key=GROQ_KEY)
notion = Client(auth=NOTION_TOKEN)

def get_existing_words():
    results = notion.databases.query(database_id=DATABASE_ID)
    words = []
    for page in results["results"]:
        title = page["properties"]["名前"]["title"]
        if title:
            words.append(title[0]["plain_text"].lower())
    return words

def translate_and_example(word):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"英単語「{word}」について以下を日本語で答えてください。\n1. 日本語訳（1行）\n2. 英語例文（1文）\n3. 例文の日本語訳（1行）\n\n形式：\n訳：〇〇\n例文：〇〇\n例文訳：〇〇"
            }
        ]
    )
    return response.choices[0].message.content

def add_word(word):
    existing = get_existing_words()
    if word.lower() in existing:
        print(f"「{word}」はすでに登録済みです\n")
        return
    print(f"「{word}」を処理中...")
    result = translate_and_example(word)
    print(result)
    today = str(datetime.date.today())
    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "名前": {"title": [{"text": {"content": word}}]},
            "意味": {"rich_text": [{"text": {"content": result}}]},
            "登録日": {"rich_text": [{"text": {"content": today}}]}
        }
    )
    print(f"Notionに保存完了！\n")

# メインループ
print("=== 英語学習自動化システム ===")
print("終了するには「quit」と入力してください\n")

while True:
    word = input("単語を入力：").strip()
    if word.lower() == "quit":
        print("終了します")
        break
    if word == "":
        continue
    add_word(word)