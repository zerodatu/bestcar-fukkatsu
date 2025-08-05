import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
from janome.tokenizer import Tokenizer, Token
import time

# 形態素解析器
tokenizer = Tokenizer()


def scrape_article(url):
    """記事本文を取得"""
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # 記事本文抽出
        article = soup.find("div", class_="article-body")
        if not article:
            return ""
        text = article.get_text(separator=" ", strip=True)
        return text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def extract_words(text: str) -> list[str]:
    """日本語の名詞を抽出"""
    words: list[str] = []
    for token in tokenizer.tokenize(text):
        if isinstance(token, Token) and token.part_of_speech.split(",")[0] == "名詞":
            words.append(token.surface)
    return words


def main():
    base_url = "https://bestcarweb.jp/news/scoop/"
    word_counter = Counter()

    # 範囲を指定（テスト用に1〜10）
    for i in range(1, 11):  # 本番は 1〜1284454
        url = f"{base_url}{i}/"
        print(f"Fetching {url} ...")
        text = scrape_article(url)
        if text:
            words = extract_words(text)
            word_counter.update(words)
        time.sleep(1)  # サーバー負荷軽減のためウェイト

    # 上位30単語を表示
    for word, count in word_counter.most_common(30):
        print(word, count)


if __name__ == "__main__":
    main()
