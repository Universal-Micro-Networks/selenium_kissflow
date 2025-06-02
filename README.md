# Kissflow Downloader

Kissflowのワークフローから添付ファイルをダウンロードするためのPythonスクリプトです。

## 必要条件

- Python 3.13.3以上
- Chromeブラウザ
- UV（Pythonパッケージマネージャー）

## UVのインストール

### Windows
```powershell
# PowerShellを使用する場合
(Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing).Content | pwsh -Command -

# または、コマンドプロンプトを使用する場合
curl -sSf https://astral.sh/uv/install.cmd | cmd
```

### macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストール後、ターミナルを再起動して`uv`コマンドが使用可能になったことを確認してください。

## セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/Universal-Micro-Networks/selenium_kissflow.git
cd selenium_kissflow
```

2. 仮想環境の作成とアクティベート

Windows:
```powershell
# PowerShell
uv venv
.venv\Scripts\Activate.ps1

# または、コマンドプロンプト
uv venv
.venv\Scripts\activate.bat
```

macOS:
```bash
uv venv
source .venv/bin/activate
```

3. 依存関係のインストール
```bash
uv pip install .
```

4. 環境変数の設定

プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下の内容を設定します：
```env
KISSFLOW_URL=https://your-domain.kissflow.com
KISSFLOW_USERNAME=your-username
KISSFLOW_PASSWORD=your-password
```

## 使用方法

1. 仮想環境のアクティベート（まだアクティベートしていない場合）

Windows:
```powershell
# PowerShell
.venv\Scripts\Activate.ps1

# または、コマンドプロンプト
.venv\Scripts\activate.bat
```

macOS:
```bash
source .venv/bin/activate
```

2. スクリプトの実行
```bash
python kissflow_downloader.py
```

3. プロンプトが表示されたら、ダウンロードしたいワークフローのURLを入力します。

4. ダウンロードされたファイルは`downloads`ディレクトリに保存されます。

## トラブルシューティング

### Chromeドライバーの問題
- Chromeブラウザが最新バージョンであることを確認してください
- スクリプトは自動的に適切なChromeドライバーをダウンロードします

### 環境変数の問題
- `.env`ファイルが正しい場所（プロジェクトのルートディレクトリ）にあることを確認
- 環境変数の値が正しく設定されていることを確認

### ダウンロードの問題
- `downloads`ディレクトリへの書き込み権限があることを確認
- ネットワーク接続が安定していることを確認

## 開発

### 型チェック
```bash
uv pip install ".[dev]"
mypy kissflow_downloader.py
```

### コードフォーマット
```bash
ruff format kissflow_downloader.py
```

### リント
```bash
ruff check kissflow_downloader.py
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
