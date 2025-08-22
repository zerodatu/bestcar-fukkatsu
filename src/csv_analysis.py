import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

# --- 定数定義 ---
CSV_FILE_PATH = 'word_occurrences_local.csv'
OUTPUT_IMAGE_PATH = 'word_frequency_graph.png'
TOP_N = 30  # 上位何件をグラフ化するか

def create_word_frequency_graph(csv_path: str, output_path: str, top_n: int):
    """
    単語出現頻度のCSVファイルを読み込み、上位N件の棒グラフを生成して保存する。

    Args:
        csv_path (str): 入力するCSVファイルのパス。
        output_path (str): 出力する画像ファイルのパス。
        top_n (int): グラフに表示する上位単語の数。
    """
    try:
        # CSVファイルをPandasのDataFrameとして読み込む
        # 3列目のファイルパスは不要なため、usecolsで最初の2列のみを指定
        df = pd.read_csv(csv_path, usecols=['単語', '出現回数'])
        print(f"'{csv_path}'の読み込みに成功しました。")

        # 「出現回数」が多い順にデータをソートし、上位N件を抽出
        top_df = df.sort_values(by='出現回数', ascending=False).head(top_n)
        print(f"出現頻度上位{top_n}件のデータを抽出しました。")

        # グラフ描画設定
        plt.figure(figsize=(12, 10))
        sns.barplot(x='出現回数', y='単語', data=top_df, palette='viridis')

        # グラフのタイトルとラベルを設定
        plt.title(f'単語の出現頻度 上位{top_n}件', fontsize=16)
        plt.xlabel('出現回数', fontsize=12)
        plt.ylabel('単語', fontsize=12)
        
        # レイアウトを調整して、ラベルが重ならないようにする
        plt.tight_layout()

        # グラフを画像ファイルとして保存
        plt.savefig(output_path)
        print(f"グラフを'{output_path}'として保存しました。")

    except FileNotFoundError:
        print(f"エラー: ファイル '{csv_path}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    create_word_frequency_graph(CSV_FILE_PATH, OUTPUT_IMAGE_PATH, TOP_N)
