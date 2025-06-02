import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class KissflowDownloader:
    def __init__(self) -> None:
        load_dotenv()
        self.base_url: str = os.getenv('KISSFLOW_URL', '')
        self.username: str = os.getenv('KISSFLOW_USERNAME', '')
        self.password: str = os.getenv('KISSFLOW_PASSWORD', '')

        if not all([self.base_url, self.username, self.password]):
            raise ValueError("必要な環境変数が設定されていません")

        self.download_dir = Path('downloads')
        self.download_dir.mkdir(exist_ok=True)

        # Chromeの設定
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            'download.default_directory': str(self.download_dir.absolute()),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        })

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 20)

    def login(self) -> None:
        """Kissflowにログインする"""
        try:
            self.driver.get(self.base_url)

            # ログインフォームの待機と入力
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys(self.username)
            password_field.send_keys(self.password)

            # ログインボタンのクリック
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # ログイン後のダッシュボード表示を待機
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard-container"))
            )
            print("ログインに成功しました")

        except TimeoutException:
            print("ログインに失敗しました")
            raise

    def download_attachments(self, workflow_url: str) -> None:
        """指定されたワークフローの添付ファイルをダウンロードする"""
        try:
            self.driver.get(workflow_url)

            # 添付ファイルのリストを待機
            attachment_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".attachment-item"))
            )

            for attachment in attachment_elements:
                file_name = None  # 初期化を追加
                try:
                    # ファイル名を取得
                    file_name = attachment.find_element(By.CSS_SELECTOR, ".attachment-name").text

                    # ダウンロードボタンをクリック
                    download_button = attachment.find_element(By.CSS_SELECTOR, ".download-button")
                    download_button.click()

                    # ダウンロードの完了を待機
                    time.sleep(2)  # ダウンロード開始の待機

                    print(f"ファイル '{file_name}' のダウンロードを開始しました")

                except Exception as e:
                    print(f"ファイル '{file_name}' のダウンロード中にエラーが発生しました: {str(e)}")
                    continue

        except TimeoutException:
            print("ワークフローページの読み込みに失敗しました")
            raise

    def close(self) -> None:
        """ブラウザを閉じる"""
        self.driver.quit()

def main() -> None:
    # 環境変数の確認
    required_env_vars = ['KISSFLOW_URL', 'KISSFLOW_USERNAME', 'KISSFLOW_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        print("'.env'ファイルに必要な環境変数を設定してください。")
        return

    downloader = KissflowDownloader()
    try:
        downloader.login()

        # ワークフローのURLを入力
        workflow_url = input("ダウンロードしたいワークフローのURLを入力してください: ")
        downloader.download_attachments(workflow_url)

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
    finally:
        downloader.close()

if __name__ == "__main__":
    main()
