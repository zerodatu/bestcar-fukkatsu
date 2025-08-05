import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from janome.tokenizer import Tokenizer, Token
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import random

# 形態素解析器
tokenizer = Tokenizer()

BASE_URL = "https://bestcarweb.jp/news/scoop/"
MAX_WORKERS = 20
BATCH_SIZE = 100_000  # 10万件単位で処理
RETRY_COUNT = 3


def scrape_article(article_id):
    """記事を取得し、(記事ID, 単語リスト)を返す"""
    url = f"{BASE_URL}{article_id}"
    for attempt in range(RETRY_COUNT):
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 404:
                return None
            if res.status_code == 500:
                print(f"500 Error: {url} → スキップ")
                return None

            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            article = soup.find("div", class_="article-body")
            if not article:
                return None

            text = article.get_text(separator=" ", strip=True)
            words = extract_words(text)
            return article_id, words
        except Exception as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(2)
            else:
                print(f"Error fetching {url}: {e}")
                return None
        time.sleep(random.uniform(0.2, 0.5))


def extract_words(text: str) -> list[str]:
    """日本語の名詞を抽出"""
    words: list[str] = []
    for token in tokenizer.tokenize(text):
        if isinstance(token, Token) and token.part_of_speech.split(",")[0] == "名詞":
            words.append(token.surface)
    return words


def process_batch(start_id, end_id):
    word_occurrences = defaultdict(list)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(scrape_article, i) for i in range(start_id, end_id + 1)]

        for future in as_completed(futures):
            result = future.result()
            if result:
                article_id, words = result
                url = f"{BASE_URL}{article_id}"
                for word in set(words):
                    word_occurrences[word].append(url)

    filename = f"word_occurrences_{start_id}_{end_id}.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["単語", "出現回数", "記事URL"])
        for word, urls in sorted(word_occurrences.items(), key=lambda x: len(x[1]), reverse=True):
            writer.writerow([word, len(urls), ", ".join(urls)])

    print(f"CSV出力完了: {filename}")


def main(start_id, end_id):
    for batch_start in range(start_id, end_id + 1, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE - 1, end_id)
        print(f"=== {batch_start} 〜 {batch_end} を処理中 ===")
        process_batch(batch_start, batch_end)
        print("バッチ完了、5秒休憩中…")
        time.sleep(5)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python main.py <START_ID> <END_ID>")
        sys.exit(1)

    start_id = int(sys.argv[1])
    end_id = int(sys.argv[2])

    start_time = time.time()
    main(start_id, end_id)
    print(f"総処理時間: {time.time() - start_time:.2f}秒")
