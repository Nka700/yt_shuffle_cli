# プロジェクト構造

```
/
├── src/
│   └── ytm/
│       ├── __init__.py        # パッケージ定義（__version__ のみ）
│       └── cli.py             # CLI 本体（main が console script のエントリポイント）
├── tests/
│   └── test_ytm.py            # pytest + hypothesis のテスト
├── legacy/                    # 移行前の資産（参考用）
│   ├── ytm                    # 旧 Python 単一ファイル版
│   ├── test_ytm.py            # 旧単一ファイル版のテスト
│   ├── mpvy                   # 旧Bashスクリプト
│   └── lsytmplylst            # 旧Bashスクリプト
├── pyproject.toml             # ビルド設定（hatchling）・バージョン・エントリポイント
├── dist/                      # ビルド成果物（git 管理外）
├── BUILD.md                   # ビルド・テスト手順
├── USAGE.md                   # 使い方ガイド
├── MIGRATION.md               # Bash→Python 移行理由ドキュメント
└── .kiro/
    ├── steering/              # AIアシスタント向けステアリングルール
    └── specs/                 # 機能仕様（playlist-name-play）
```

## 設計方針

- **CLI 実装は `cli.py` に集約**: パッケージ `src/ytm/` 配下だが、実装ロジックは `cli.py` 1ファイルに置き、それ以上モジュール分割しない
- **エントリポイント**: `pyproject.toml` の `[project.scripts]` で `ytm = "ytm.cli:main"`。インストールして `ytm` コマンドとして実行する
- **バージョン管理**: `pyproject.toml` の `version` と `src/ytm/__init__.py` の `__version__` を同じ値に保つ
- **サブコマンド形式**: `argparse` の `add_subparsers` で `playlists` / `play` を統合
- **外部コマンドは subprocess 経由**: mpv / yt-dlp は Python で代替しない

## コードスタイル

- 日本語のドキュメント文字列・コメント
- 画面・stderr への出力メッセージ（エラー・警告・ヘルプ文を含む）は英語。文字化け防止のため絵文字・全角記号などの非 ASCII 文字も使わない（警告は `WARNING:` 接頭辞）
- 関数名・変数名は英語（Python標準の snake_case）
- 内部用の関数・定数は `_` プレフィックス（例: `_get_env`, `_cookies_args`, `_check_ytdlp_version`, `_print_resolved`）。サブコマンド実装は `cmd_` プレフィックス（`cmd_playlists`, `cmd_play`）
- エラー出力は `sys.stderr` に出力し、`sys.exit(1)` で終了
- 型ヒントは引数・戻り値に付与（`list[dict]` など組み込みジェネリクス形式）
- `cli.py` 内はコメントの区切り線でセクション分けする（設定 / YouTube Data API / playlists / プレイリスト名前解決 / play / メイン）

## ログ出力

- mpv のログ: `~/log/mpv_YYYYMMDD_HHMM.log`（`~/log` が無ければ自動作成）
