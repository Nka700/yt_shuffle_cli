# 技術スタック

## 言語

- **Python 3.8+**（shebang: `#!/usr/bin/env python3`）

## 外部コマンド依存

| コマンド | 用途 | 必須 |
|---------|------|------|
| `mpv` | 音声再生（`play` サブコマンド） | play 時のみ |
| `yt-dlp` | YouTube音声ストリーミング（mpv の ytdl_hook 経由） | play 時のみ |

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
| `datetime` | ログファイル名生成、yt-dlp バージョン判定 |

## API

- YouTube Data API v3（プレイリスト一覧取得）

## 認証情報

- `$KEY_API_YOUTUBE` — YouTube API キー（環境変数）
- `$CHANNELID_API_YOUTUBE` — チャンネル ID（環境変数）

## クッキー（オプション）

- `~/.config/ytm/cookies.txt` — yt-dlp / mpv 用のブラウザクッキー（ボット検出回避用）

## よく使うコマンド

```bash
# プレイリスト一覧を表示
./ytm playlists

# シェル変数としてエクスポート
eval $(./ytm playlists --export)

# プレイリストをシャッフル音声再生
./ytm play <playlist_id>
```

## ビルド・テスト

- ビルドシステムなし。`ytm` を直接実行する
- テストフレームワークなし
- 外部 pip パッケージ依存なし
