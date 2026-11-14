# プロダクト概要

YouTube関連のCLIユーティリティ `ytm`。個人用ターミナルツール。

## 機能

| サブコマンド | 説明 |
|-------------|------|
| `ytm playlists` | YouTube Data API v3 でチャンネルの全プレイリストを取得・表示（ページネーション対応） |
| `ytm playlists --export` | `eval $(ytm playlists --export)` でシェル変数にエクスポート可能な形式で出力 |
| `ytm play <playlist>` | mpv + yt-dlp でプレイリストをシャッフル音声再生。`<playlist>` はプレイリスト ID（`PL` 始まり）、Shell_Varname（例: `YTM_MY_PLAYLIST`）、元タイトル（大文字小文字不問）のいずれか |

## 経緯

元は2つの独立したBashスクリプト（`lsytmplylst`, `mpvy`）で構成されていた。
`source lsytmplylst` でプレイリストをシェル変数に読み込み、`mpvy $変数` で再生する使い方だった。
`MIGRATION.md` の方針に従い、依存関係の削減・ページネーション対応・エラーハンドリング改善のため Python に移行・統合した。
その後 `pyproject.toml`（hatchling）によるパッケージ構成（`src/ytm/`）に変更し、`ytm` コマンドとしてインストールして使う形になった。
プレイリスト名での再生（名前解決）は `.kiro/specs/playlist-name-play/` で仕様化している。
