import os
from bs4 import BeautifulSoup
from collections import defaultdict
from janome.tokenizer import Tokenizer, Token
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 形態素解析器
tokenizer = Tokenizer()

DOWNLOAD_DIR = "download"  # HTML保存フォルダ
MAX_WORKERS = 20  # スレッド数（CPUコア数に応じて調整）


def extract_words(text: str) -> list[str]:
    """日本語の名詞を抽出"""
    words: list[str] = []
    for token in tokenizer.tokenize(text):
        if isinstance(token, Token) and token.part_of_speech.split(",")[0] == "名詞":
            words.append(token.surface)
    return words


def parse_html_file(file_name: str):
    """1つのHTMLファイルを解析して(単語, ファイルパス)のマッピングを返す"""
    file_path = os.path.join(DOWNLOAD_DIR, file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "lxml")
            article = soup.find("div", class_="article-body")
            if not article:
                return None

            text = article.get_text(separator=" ", strip=True)
            words = extract_words(text)
            return file_path, set(words)  # 重複排除した単語
    except Exception as e:
        print(f"Error parsing {file_name}: {e}")
        return None


def main():
    start_time = time.time()
    word_occurrences = defaultdict(list)

    html_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".html")]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(parse_html_file, file) for file in html_files]

        for future in tqdm(as_completed(futures), total=len(futures), desc="解析中"):
            result = future.result()
            if result:
                file_path, words = result
                for word in words:
                    word_occurrences[word].append(file_path)

    # CSV書き出し
    filename = "word_occurrences_local.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["単語", "出現回数", "ファイルパス"])
        for word, paths in sorted(
            word_occurrences.items(), key=lambda x: len(x[1]), reverse=True
        ):
            writer.writerow([word, len(paths), ", ".join(paths)])

    print(f"CSV出力完了: {filename}")
    print(f"処理時間: {time.time() - start_time:.2f}秒")


if __name__ == "__main__":
    main()
