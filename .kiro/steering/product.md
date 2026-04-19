# プロダクト概要

YouTube関連のCLIユーティリティ `ytm`。個人用ターミナルツール。

## 機能

| サブコマンド | 説明 |
|-------------|------|
| `ytm playlists` | YouTube Data API v3 でチャンネルの全プレイリストを取得・表示（ページネーション対応） |
| `ytm playlists --export` | `eval $(ytm playlists --export)` でシェル変数にエクスポート可能な形式で出力 |
| `ytm play <playlist_id>` | mpv + yt-dlp でプレイリストをシャッフル音声再生 |

## 経緯

元は2つの独立したBashスクリプト（`lsytmplylst`, `mpvy`）で構成されていた。
`source lsytmplylst` でプレイリストをシェル変数に読み込み、`mpvy $変数` で再生する使い方だった。
`MIGRATION.md` の方針に従い、依存関係の削減・ページネーション対応・エラーハンドリング改善のため Python 単一ファイルに移行・統合した。
