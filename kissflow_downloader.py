import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def load_environment() -> tuple[str, str, str]:
    """環境変数を読み込み、必要な変数が設定されているか確認する"""
    load_dotenv(override=True)  # 既存の環境変数を上書き

    base_url = os.getenv('KISSFLOW_URL')
    username = os.getenv('KISSFLOW_USERNAME')
    password = os.getenv('KISSFLOW_PASSWORD')

    missing_vars = []
    if not base_url:
        missing_vars.append('KISSFLOW_URL')
    if not username:
        missing_vars.append('KISSFLOW_USERNAME')
    if not password:
        missing_vars.append('KISSFLOW_PASSWORD')

    if missing_vars:
        raise ValueError(
            f"以下の環境変数が設定されていません: {', '.join(missing_vars)}\n"
            "'.env'ファイルに必要な環境変数を設定してください。"
        )

    # この時点で全ての変数がNoneでないことが保証されている
    return str(base_url), str(username), str(password)


class KissflowDownloader:
    def __init__(self) -> None:
        self.base_url, self.username, self.password = load_environment()
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

        # デバッグ用の設定
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # chrome_options.add_argument('--headless')  # 必要に応じてコメントを外す

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 30)  # タイムアウトを30秒に延長

        # 自動化検出を回避
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })

    def _wait_and_find_element(self, by: By, value: str, timeout: int = 30) -> webdriver.remote.webelement.WebElement:
        """要素を待機して見つける"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"要素が見つかりません: {by}={value}")
            print(f"現在のURL: {self.driver.current_url}")
            print(f"ページソース: {self.driver.page_source[:500]}...")  # 最初の500文字のみ表示
            raise

    def login(self) -> None:
        """Kissflowにログインする"""
        try:
            print(f"ログインページにアクセス: {self.base_url}")
            self.driver.get(self.base_url)

            # ページの読み込みを待機
            time.sleep(5)  # 初期読み込みの待機時間を延長

            print("ログインフォームを探しています...")

            # ユーザー名フィールドの待機と入力
            try:
                # 複数のセレクターを試す
                selectors = [
                    (By.ID, "email"),
                ]

                username_field = None
                for by, value in selectors:
                    try:
                        username_field = self._wait_and_find_element(by, value)
                        print(f"ユーザー名フィールドが見つかりました: {by}={value}")
                        break
                    except TimeoutException:
                        continue

                if username_field is None:
                    raise NoSuchElementException("ユーザー名フィールドが見つかりません")

                username_field.clear()
                username_field.send_keys(self.username)
                print("ユーザー名を入力しました")
            except Exception as e:
                print(f"ユーザー名フィールドの処理中にエラー: {str(e)}")
                raise

            # パスワードフィールドの待機と入力
            try:
                # 複数のセレクターを試す
                selectors = [
                    (By.ID, "password"),
                ]

                password_field = None
                for by, value in selectors:
                    try:
                        password_field = self._wait_and_find_element(by, value)
                        print(f"パスワードフィールドが見つかりました: {by}={value}")
                        break
                    except TimeoutException:
                        continue

                if password_field is None:
                    raise NoSuchElementException("パスワードフィールドが見つかりません")

                password_field.clear()
                password_field.send_keys(self.password)
                print("パスワードを入力しました")
            except Exception as e:
                print(f"パスワードフィールドの処理中にエラー: {str(e)}")
                raise

            # reCAPTCHAの待機（存在する場合）
            try:
                recaptcha = self.driver.find_element(By.CLASS_NAME, "g-recaptcha")
                if recaptcha.is_displayed():
                    print("reCAPTCHAが検出されました。手動での入力を待機します...")
                    input("reCAPTCHAを完了したらEnterキーを押してください...")
            except NoSuchElementException:
                print("reCAPTCHAは検出されませんでした")

            # ログインボタンの待機とクリック
            try:
                # 複数のセレクターを試す
                selectors = [
                    (By.CSS_SELECTOR, "button[data-component='button']"),
                ]

                login_button = None
                for by, value in selectors:
                    try:
                        login_button = self._wait_and_find_element(by, value)
                        print(f"ログインボタンが見つかりました: {by}={value}")
                        break
                    except TimeoutException:
                        continue

                if login_button is None:
                    raise NoSuchElementException("ログインボタンが見つかりません")

                login_button.click()
                print("ログインボタンをクリックしました")
            except Exception as e:
                print(f"ログインボタンの処理中にエラー: {str(e)}")
                raise

            # ログイン後のダッシュボード表示を待機
            try:
                # 複数のセレクターを試す
                selectors = [
                    (By.CSS_SELECTOR, ".dashboard-container"),
                    (By.CSS_SELECTOR, ".app-container"),
                    (By.CSS_SELECTOR, ".workspace-container")
                ]

                for by, value in selectors:
                    try:
                        self.wait.until(EC.presence_of_element_located((by, value)))
                        print(f"ダッシュボードの読み込みが完了しました: {by}={value}")
                        break
                    except TimeoutException:
                        continue
                else:
                    raise TimeoutException("ダッシュボードの読み込みがタイムアウトしました")

            except TimeoutException:
                print("ダッシュボードの読み込みがタイムアウトしました")
                print(f"現在のURL: {self.driver.current_url}")
                print(f"ページソース: {self.driver.page_source[:500]}...")
                raise

            print("ログインに成功しました")

        except WebDriverException as e:
            print(f"WebDriverエラー: {str(e)}")
            raise
        except Exception as e:
            print(f"予期せぬエラー: {str(e)}")
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
    downloader: Optional[KissflowDownloader] = None
    try:
        downloader = KissflowDownloader()
        downloader.login()

        # ワークフローのURLを入力
        workflow_url = input("ダウンロードしたいワークフローのURLを入力してください: ")
        downloader.download_attachments(workflow_url)

    except ValueError as e:
        print(f"設定エラー: {str(e)}")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
    finally:
        if downloader is not None:
            downloader.close()

if __name__ == "__main__":
    main()
