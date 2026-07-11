"""
ytm - YouTube Music CLI ユーティリティ

サブコマンド:
  playlists            チャンネルのプレイリスト一覧を表示
  playlists --export   シェル変数としてエクスポート可能な形式で出力
  play <playlist_id>   プレイリストをシャッフル音声再生
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------

def _get_env(name: str) -> str:
    """環境変数から認証情報を取得する。未設定ならエラー終了"""
    value = os.environ.get(name)
    if not value:
        print(f"エラー: 環境変数 {name} が設定されていません。", file=sys.stderr)
        sys.exit(1)
    return value


def get_api_key() -> str:
    return _get_env("KEY_API_YOUTUBE")


def get_channel_id() -> str:
    return _get_env("CHANNELID_API_YOUTUBE")


# ---------------------------------------------------------------------------
# YouTube Data API
# ---------------------------------------------------------------------------

def youtube_api_get(endpoint: str, params: dict) -> dict:
    """YouTube Data API v3 に GET リクエストを送る"""
    query = urllib.parse.urlencode(params)
    url = f"https://youtube.googleapis.com/youtube/v3/{endpoint}?{query}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"APIエラー (HTTP {e.code}): {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ネットワークエラー: {e.reason}", file=sys.stderr)
        sys.exit(1)


COOKIES_PATH = Path.home() / ".config" / "ytm" / "cookies.txt"


def _check_ytdlp_version() -> None:
    """yt-dlp のバージョンを確認し、古い場合は警告する"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--version"], capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            # バージョンは YYYY.MM.DD 形式
            try:
                ver_date = datetime.strptime(version, "%Y.%m.%d")
                age_days = (datetime.now() - ver_date).days
                if age_days > 90:
                    print(
                        f"⚠️  yt-dlp のバージョンが古いです ({version}, {age_days}日前)\n"
                        f"   YouTubeの変更により再生に失敗する可能性があります。\n"
                        f"   更新: pip install -U yt-dlp  または  yt-dlp -U\n",
                        file=sys.stderr,
                    )
            except ValueError:
                pass
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def _cookies_args() -> list[str]:
    """クッキーファイルが存在すれば、yt-dlp/mpv 用の引数を返す"""
    if COOKIES_PATH.is_file():
        return [f"--cookies={COOKIES_PATH}"]
    return []


# ---------------------------------------------------------------------------
# playlists サブコマンド
# ---------------------------------------------------------------------------

def fetch_all_playlists(channel_id: str, api_key: str) -> list[dict]:
    """ページネーション対応で全プレイリストを取得する"""
    playlists = []
    page_token = None

    while True:
        params = {
            "part": "id,snippet",
            "channelId": channel_id,
            "maxResults": 50,
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token

        data = youtube_api_get("playlists", params)

        for item in data.get("items", []):
            playlists.append({
                "title": item["snippet"]["title"],
                "id": item["id"],
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return playlists


def to_shell_varname(title: str) -> str:
    """プレイリストタイトルをシェル変数名に変換する"""
    name = title.upper()
    name = re.sub(r"[^A-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")
    return f"YTM_{name}"


def cmd_playlists(args: argparse.Namespace) -> None:
    api_key = get_api_key()
    channel_id = get_channel_id()

    playlists = fetch_all_playlists(channel_id, api_key)

    if not playlists:
        print("プレイリストが見つかりませんでした。", file=sys.stderr)
        return

    if args.export:
        # source $(ytm playlists --export) 用のシェル変数出力
        for pl in playlists:
            varname = to_shell_varname(pl["title"])
            print(f'export {varname}="{pl["id"]}"')
    else:
        print("YouTube Music Playlists:")
        print("-" * 60)
        for pl in playlists:
            varname = to_shell_varname(pl["title"])
            print(f"  {varname:<40s} {pl['id']}")
        print(f"\n合計: {len(playlists)} 件")


# ---------------------------------------------------------------------------
# プレイリスト名前解決
# ---------------------------------------------------------------------------

def _print_resolved(playlist: dict) -> None:
    """解決されたプレイリスト情報を stderr に表示する。"""
    print(f'🎵 プレイリスト解決: "{playlist["title"]}" ({playlist["id"]})', file=sys.stderr)


def _print_no_match_error(name: str, playlists: list) -> None:
    """一致しなかった場合のエラーメッセージと利用可能なプレイリスト一覧を stderr に表示し終了する。"""
    print(f'エラー: "{name}" に一致するプレイリストが見つかりません。', file=sys.stderr)
    print(file=sys.stderr)
    print("利用可能なプレイリスト:", file=sys.stderr)
    for pl in playlists:
        varname = to_shell_varname(pl["title"])
        print(f"  {varname:<40s} {pl['title']}", file=sys.stderr)
    sys.exit(1)


def resolve_playlist_id(name: str) -> str:
    """プレイリスト名または ID を受け取り、プレイリスト ID に解決する。

    解決の優先順位:
      1. PL で始まる文字列 → そのまま返す（API 呼び出しなし）
      2. Shell_Varname 完全一致
      3. 元タイトル case-insensitive 完全一致
    一致しない場合はエラーメッセージを表示して sys.exit(1)。
    """
    # 1. PL で始まる → 直接返す
    if name.startswith("PL"):
        return name

    # 2. API で全プレイリスト取得
    api_key = get_api_key()
    channel_id = get_channel_id()
    playlists = fetch_all_playlists(channel_id, api_key)

    # 3. Shell_Varname 完全一致
    for pl in playlists:
        if to_shell_varname(pl["title"]) == name:
            _print_resolved(pl)
            return pl["id"]

    # 4. 元タイトル case-insensitive 完全一致
    name_lower = name.lower()
    for pl in playlists:
        if pl["title"].lower() == name_lower:
            _print_resolved(pl)
            return pl["id"]

    # 5. 一致なし → エラー
    _print_no_match_error(name, playlists)


# ---------------------------------------------------------------------------
# play サブコマンド
# ---------------------------------------------------------------------------

def cmd_play(args: argparse.Namespace) -> None:
    # プレイリスト名/IDを解決
    playlist_id = resolve_playlist_id(args.playlist)

    # 依存コマンドの存在確認
    for cmd in ("yt-dlp", "mpv"):
        if not shutil.which(cmd):
            print(f"エラー: {cmd} が見つかりません。インストールしてください。", file=sys.stderr)
            sys.exit(1)

    _check_ytdlp_version()

    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    cookies = _cookies_args()

    # プレイリスト情報を表示
    print("プレイリスト情報を取得中...")
    try:
        yt_cmd = ["yt-dlp", "--flat-playlist", "--dump-json"] + cookies + [playlist_url]
        result = subprocess.run(yt_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            total = 0
            unavailable = 0
            for line in result.stdout.strip().splitlines():
                try:
                    entry = json.loads(line)
                    idx = entry.get("playlist_index", "?")
                    title = entry.get("title", "(不明)")
                    total += 1
                    if title in ("[Deleted video]", "[Private video]"):
                        unavailable += 1
                        print(f"  [{idx}] {title} (スキップ)")
                    else:
                        print(f"  [{idx}] {title}")
                except json.JSONDecodeError:
                    continue
            if unavailable:
                print(f"\n  ※ {unavailable}/{total} 件の動画が利用不可")
        else:
            stderr_msg = result.stderr.strip()
            if "Sign in" in stderr_msg or "bot" in stderr_msg:
                print(
                    "⚠️ YouTubeのボット検出に引っかかっています。\n"
                    "   対処法:\n"
                    "   1. yt-dlp を最新版に更新: pip install -U yt-dlp\n"
                    "   2. ブラウザのクッキーを使用:\n"
                    f"      yt-dlp --cookies-from-browser chrome --cookies {COOKIES_PATH}\n"
                    f"      (クッキーは {COOKIES_PATH} に保存されます)",
                    file=sys.stderr,
                )
            else:
                print(f"⚠️ プレイリスト情報の取得に失敗しました。\n{stderr_msg}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("⚠️ プレイリスト情報の取得がタイムアウトしました。", file=sys.stderr)

    # mpv で再生
    print("\n再生中... q で停止")
    log_dir = Path.home() / "log"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"mpv_{datetime.now():%Y%m%d_%H%M}.log"

    # mpv に渡す ytdl_hook 用のクッキー設定
    ytdl_raw_options_parts = []
    if cookies:
        ytdl_raw_options_parts.append(f"cookies={COOKIES_PATH}")

    mpv_cmd = [
        "mpv",
        f"--log-file={log_file}",
        "--no-config",
        "--no-video",
        "--shuffle",
        "--ytdl-format=bestaudio",
        "--script-opts=ytdl_hook-ytdl_path=yt-dlp",
        *(
            [f"--ytdl-raw-options={','.join(ytdl_raw_options_parts)}"]
            if ytdl_raw_options_parts
            else []
        ),
        "--term-playing-msg=Title: ${media-title}",
        playlist_url,
    ]
    subprocess.run(mpv_cmd)


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ytm",
        description="YouTube Music CLI ユーティリティ",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # playlists
    p_pl = subparsers.add_parser("playlists", help="プレイリスト一覧を表示")
    p_pl.add_argument(
        "--export", action="store_true",
        help="シェル変数エクスポート形式で出力 (eval $(ytm playlists --export) で利用)",
    )
    p_pl.set_defaults(func=cmd_playlists)

    # play
    p_play = subparsers.add_parser("play", help="プレイリストをシャッフル音声再生")
    p_play.add_argument(
        "playlist",
        help="プレイリスト ID（PL で始まる文字列）、プレイリスト名（Shell_Varname 形式または元タイトル）",
    )
    p_play.set_defaults(func=cmd_play)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
