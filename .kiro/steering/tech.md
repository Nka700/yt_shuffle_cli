# 技術スタック

## 言語

- **Python 3.9+**（`cli.py` が `list[dict]` など組み込みジェネリクスを評価時に使うため。`pyproject.toml` の `requires-python` は `>=3.8` だが、コードの実態は 3.9 以上が必要）
- 開発環境は `.python-version` で 3.13 系、`.venv` を使用

## 外部コマンド依存

| コマンド | 用途 | 必須 |
|---------|------|------|
| `mpv` | 音声再生（`play` サブコマンド）。`--no-config --no-video --shuffle --ytdl-format=bestaudio` で起動 | play 時のみ |
| `yt-dlp` | プレイリスト情報取得、YouTube音声ストリーミング（mpv の ytdl_hook 経由） | play 時のみ |

`play` 実行時に `yt-dlp` / `mpv` が PATH に無ければエラー終了する。`yt-dlp` のバージョンが90日より古い場合は警告を表示する。

## 使用する標準ライブラリ

| モジュール | 用途 |
|-----------|------|
| `urllib.request` / `urllib.parse` / `urllib.error` | YouTube Data API v3 への HTTP リクエスト |
| `json` | JSON パース |
| `argparse` | CLI サブコマンド解析 |
| `subprocess` | mpv / yt-dlp の呼び出し |
| `pathlib.Path` | ファイルパス操作 |
| `shutil.which` | 外部コマンドの存在確認 |
| `re` | 正規表現（シェル変数名変換） |
| `os` | 環境変数の取得 |
| `sys` | stderr 出力、終了コード |
| `datetime` | ログファイル名生成、yt-dlp バージョン判定 |

## API

- YouTube Data API v3（`playlists` エンドポイントでプレイリスト一覧取得。`playlists` サブコマンドと、`play` の名前解決で使用）

## 認証情報

- `$KEY_API_YOUTUBE` — YouTube API キー（環境変数）
- `$CHANNELID_API_YOUTUBE` — チャンネル ID（環境変数）

`playlists` と、名前での `play`（`PL` で始まらない引数）で必須。未設定ならエラー終了する。`PL` で始まる ID を直接渡す `play` では API を呼ばないため不要。

## クッキー（オプション）

- `~/.config/ytm/cookies.txt` — yt-dlp / mpv 用のブラウザクッキー（ボット検出回避用）。存在する場合のみ自動で使用する

## よく使うコマンド

```bash
# 開発用インストール（ytm コマンドが PATH に追加される）
pip install -e .

# プレイリスト一覧を表示
ytm playlists

# シェル変数としてエクスポート
eval $(ytm playlists --export)

# プレイリストをシャッフル音声再生（ID / Shell_Varname / 元タイトル）
ytm play <playlist>

# テスト実行
python3 -m pytest tests/ -v
```

## ビルド・テスト

- ビルド: `pyproject.toml`（ビルドバックエンド hatchling）。`python3 -m build` で `dist/` に wheel と sdist を生成（詳細は `BUILD.md`）
- テスト: pytest + hypothesis（`tests/test_ytm.py`）。`pyproject.toml` の `testpaths = ["tests"]`
- 実行時の pip パッケージ依存なし（標準ライブラリのみ）。pytest / hypothesis は開発時のみで、`pyproject.toml` には宣言していない
