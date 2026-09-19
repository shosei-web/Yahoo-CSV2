import time
from playwright.sync_api import sync_playwright


def run():
    with sync_playwright() as p:
        # headless=False で実際のブラウザ画面を表示
        # slow_mo=500 で各操作の間に0.5秒のウェイトを入れ、動きを見やすくする
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("1. Wikipedia（日本語版）へアクセス中...")
        page.goto("https://ja.wikipedia.org/")

        print("2. 検索ボックスに『Python』と入力中...")
        page.fill('input[name="search"]', "Python")

        print("3. 検索を実行...")
        page.keyboard.press("Enter")

        # ページ遷移と描画を待機
        time.sleep(2)

        # 4. 遷移後の見出しテキストを取得
        heading = page.text_content("h1#firstHeading")
        print(f"\n★ 取得した記事タイトル: 【{heading}】")

        print("4. スクリーンショットを保存中...")
        page.screenshot(path="wiki_python.png")

        print("5. ブラウザを閉じます...")
        browser.close()

    print("\n完了！ wiki_python.png が保存されました。")


if __name__ == "__main__":
    run()