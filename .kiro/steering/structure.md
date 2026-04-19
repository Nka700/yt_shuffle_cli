# プロジェクト構造

```
/
├── ytm                        # 統合CLIツール（Python単一ファイル、実行可能）
├── MIGRATION.md               # Bash→Python 移行理由ドキュメント
├── mpvy                       # 旧Bashスクリプト（移行済み、参考用）
├── lsytmplylst                # 旧Bashスクリプト（移行済み、参考用）
└── .kiro/
    └── steering/              # AIアシスタント向けステアリングルール
```

## 設計方針

- **単一ファイル構成**: エントリポイントは `ytm` のみ。モジュール分割しない
- **サブコマンド形式**: `argparse` の `add_subparsers` で `playlists` / `play` を統合
- **外部コマンドは subprocess 経由**: mpv / yt-dlp は Python で代替しない

## コードスタイル

- 日本語のドキュメント文字列・コメント・エラーメッセージ
- 関数名・変数名は英語（Python標準の snake_case）
- プライベート関数は `_` プレフィックス（例: `_read_secret`, `_cookies_args`）
- エラー出力は `sys.stderr` に出力し、`sys.exit(1)` で終了
- 型ヒントは最小限（戻り値型のみ）

## ログ出力

- mpv のログ: `~/log/mpv_YYYYMMDD_HHMM.log`
