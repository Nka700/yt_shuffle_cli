# ytm 使い方ガイド

YouTube Music CLI ユーティリティ。プレイリストの一覧表示とシャッフル音声再生を行う。

## 前提条件

| 項目 | 説明 |
|------|------|
| Python 3.8+ | 実行環境 |
| mpv | 音声再生 |
| yt-dlp | YouTube 音声ストリーミング（mpv の ytdl_hook 経由） |
| YouTube API キー | `~/.ssh/key_api_youtube` に配置 |
| 自分のアカウントのチャンネル ID | `~/.ssh/channelid_api_youtube` に配置 |

### オプション

- `~/.config/ytm/cookies.txt` — yt-dlp / mpv 用のブラウザクッキー（ボット検出回避用）

## サブコマンド

### `ytm playlists` — プレイリスト一覧表示

```bash
# 一覧表示
./ytm playlists

# シェル変数としてエクスポート
eval $(./ytm playlists --export)
```

`--export` を付けると `export YTM_変数名="PLxxxxxx"` 形式で出力される。`eval` で読み込めばシェル変数として使える。

### `ytm play` — プレイリスト再生

引数にはプレイリスト ID、シェル変数名、または元タイトルを指定できる。

```bash
# プレイリスト ID で再生（PL で始まる文字列）
./ytm play PLxxxxxxxxxxxxxxxx

# シェル変数名（Shell_Varname）で再生
./ytm play YTM_MY_PLAYLIST

# 元タイトルで再生（大文字小文字は区別しない）
./ytm play "My Playlist"
```

## 名前解決の仕組み

`play` に渡された引数は以下の優先順位で解決される:

1. **PL プレフィックス** — `PL` で始まる文字列はプレイリスト ID としてそのまま使用（API 呼び出しなし）
2. **Shell_Varname 完全一致** — `to_shell_varname(タイトル)` と完全一致する場合、そのプレイリストを使用
3. **元タイトル一致** — プレイリストの元タイトルと大文字小文字を無視して完全一致する場合、そのプレイリストを使用

名前で解決された場合、どのプレイリストが選ばれたかが stderr に表示される:

```
🎵 プレイリスト解決: "My Playlist" (PLxxxxxxxxxxxxxxxx)
```

一致するプレイリストがない場合、利用可能なプレイリスト一覧がエラーとともに表示される。

## Shell_Varname の命名規則

元タイトルから以下のルールで変換される:

- 全て大文字に変換
- 英数字と `_` 以外の文字は `_` に置換
- 連続する `_` は 1 つにまとめる
- 先頭・末尾の `_` を除去
- `YTM_` プレフィックスを付与

例: `"My Playlist 2024"` → `YTM_MY_PLAYLIST_2024`

## 使用例

```bash
# まずプレイリスト一覧を確認
./ytm playlists

# 出力例:
#   YTM_MY_PLAYLIST                          PLxxxxxxxxxxxxxxxx
#   YTM_FAVORITES                            PLyyyyyyyyyyyyyyyyyy
#   合計: 2 件

# 好きな方法で再生
./ytm play YTM_MY_PLAYLIST
./ytm play "My Playlist"
./ytm play PLxxxxxxxxxxxxxxxx
```
