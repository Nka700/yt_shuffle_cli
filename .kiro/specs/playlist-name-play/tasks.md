# Implementation Tasks (実装タスク)

## Task 1: `resolve_playlist_id` 関数の実装

- [x] 1.1 `resolve_playlist_id(name: str) -> str` 関数を `ytm` ファイルに追加する。PL で始まる文字列はそのまま返す。それ以外は `fetch_all_playlists` で全プレイリストを取得し、Shell_Varname 完全一致 → 元タイトル case-insensitive 完全一致の優先順位で検索する。
- [x] 1.2 `_print_resolved(playlist: dict) -> None` ヘルパー関数を追加する。解決されたプレイリストのタイトルと ID を stderr に表示する（形式: `🎵 プレイリスト解決: "タイトル" (ID)`）。
- [x] 1.3 `_print_no_match_error(name: str, playlists: list[dict]) -> None` ヘルパー関数を追加する。一致しなかった場合のエラーメッセージと利用可能なプレイリスト一覧を stderr に表示し `sys.exit(1)` で終了する。

## Task 2: `cmd_play` の変更

- [x] 2.1 `cmd_play` 関数の先頭で `args.playlist` を `resolve_playlist_id` に渡し、解決済み ID を取得するように変更する。以降の処理では解決済み ID を使用する。
- [x] 2.2 `argparse` の `play` サブコマンド定義を更新する。引数名を `playlist_id` から `playlist` に変更し、ヘルプ文にプレイリスト名（Shell_Varname 形式または元タイトル）も受け付ける旨を記載する。

## Task 3: テスト環境のセットアップとプロパティテストの実装

- [x] 3.1 `test_ytm.py` ファイルをプロジェクトルートに作成し、pytest と hypothesis のインポートおよび `ytm` モジュールのインポート設定を行う。
- [x] 3.2 Property 1 のテストを実装する: PL で始まる任意の文字列に対して `resolve_playlist_id` がそのまま返し、API 呼び出しを行わないことを検証する。 [**PBT**: Feature: playlist-name-play, Property 1: PL プレフィックス文字列のパススルー]
- [x] 3.3 Property 2 のテストを実装する: ランダムなプレイリストリストから Shell_Varname で検索し、正しい ID が返ることを検証する。 [**PBT**: Feature: playlist-name-play, Property 2: Shell_Varname による解決]
- [x] 3.4 Property 3 のテストを実装する: ランダムなプレイリストリストから元タイトルの大文字小文字を変更して検索し、正しい ID が返ることを検証する。 [**PBT**: Feature: playlist-name-play, Property 3: 元タイトルの大文字小文字無視による解決]
- [x] 3.5 Property 4 のテストを実装する: どのプレイリストにも一致しない文字列に対して `sys.exit(1)` が呼ばれることを検証する。 [**PBT**: Feature: playlist-name-play, Property 4: 一致なしエラー]
- [x] 3.6 Property 5 のテストを実装する: Shell_Varname と元タイトルの両方に一致する場合に Shell_Varname 一致が優先されることを検証する。 [**PBT**: Feature: playlist-name-play, Property 5: 解決の優先順位]
- [x] 3.7 ユニットテストを実装する: API エラー時の終了、ネットワークエラー時の終了、ヘルプ文の更新確認。
- [x] 3.8 全テストを実行し、パスすることを確認する。
