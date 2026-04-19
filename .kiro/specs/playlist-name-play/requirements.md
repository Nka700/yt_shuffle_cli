# Requirements Document (要件定義)

## Introduction

`ytm play` コマンドにおいて、YouTube プレイリスト ID の代わりにプレイリスト名（シェル変数名形式）を引数として渡せるようにする機能。現在は `eval $(ytm playlists --export)` でシェル変数にエクスポートしてから ID を指定する必要があるが、この機能により `ytm play プレイリスト名` だけで再生できるようになり、操作手順を簡略化する。

## Glossary (用語)

- **CLI**: `ytm` コマンドラインツール本体
- **Name_Resolver**: CLI 内部でプレイリスト名から YouTube プレイリスト ID への変換を行うロジック
- **Shell_Varname**: `to_shell_varname` 関数が生成するシェル変数名形式の文字列（例: `YTM_MY_PLAYLIST`）
- **Playlist_ID**: YouTube プレイリストの一意識別子（`PL` で始まる文字列）
- **YouTube_API**: YouTube Data API v3

## Requirements (要件)

### Requirement 1: プレイリスト名による再生

**User Story:** ユーザーとして、プレイリスト ID を覚えなくてもプレイリスト名で直接再生したい。これにより `eval` + `export` の手順を省略できる。

#### Acceptance Criteria (受け入れ基準)

1. ユーザーが Playlist_ID 形式（`PL` で始まる文字列）を引数に渡した場合、従来通り Playlist_ID として直接使用して再生を開始する
2. ユーザーが Playlist_ID 形式でない文字列を引数に渡した場合、YouTube_API を呼び出してチャンネルの全プレイリストを取得し、引数に一致するプレイリストを検索する
3. 引数が シェル変数 形式（例: `YTM_MY_PLAYLIST`）に一致するプレイリストが見つかった場合、対応する Playlist_ID を返す
4. 引数がプレイリストの元タイトルに大文字小文字を無視して一致するプレイリストが見つかった場合、対応する Playlist_ID を返す
5. 引数に一致するプレイリストが見つからなかった場合、利用可能なプレイリスト名の一覧をエラーメッセージとともに標準エラー出力に表示し、終了コード 1 で終了する

### Requirement 2: 名前解決の優先順位

**User Story:** ユーザーとして、曖昧さなく正しいプレイリストが選択されることを期待する。

#### Acceptance Criteria (受け入れ基準)

1. THE Name_Resolver SHALL 以下の優先順位で引数を解釈する: (1) Playlist_ID 形式の直接使用、(2) Shell_Varname の完全一致、(3) 元タイトルの大文字小文字無視の完全一致
2. WHEN 複数の一致候補が存在する場合、THE Name_Resolver SHALL 最初に一致した優先順位の結果を使用する

### Requirement 3: API エラー時のフォールバック

**User Story:** ユーザーとして、API 呼び出しが失敗した場合でも適切なエラーメッセージを受け取りたい。

#### Acceptance Criteria (受け入れ基準)

1. IF YouTube_API の呼び出しが失敗した場合、THEN THE CLI SHALL エラーの詳細を標準エラー出力に表示し、終了コード 1 で終了する
2. IF YouTube_API の呼び出しがネットワークエラーで失敗した場合、THEN THE CLI SHALL ネットワークエラーである旨を標準エラー出力に表示し、終了コード 1 で終了する

### Requirement 4: 解決されたプレイリスト情報の表示

**User Story:** ユーザーとして、名前解決が行われた場合にどのプレイリストが選択されたか確認したい。

#### Acceptance Criteria (受け入れ基準)

1. WHEN Name_Resolver がプレイリスト名から Playlist_ID を解決した場合、THE CLI SHALL 解決されたプレイリストのタイトルと Playlist_ID を標準エラー出力に表示してから再生を開始する
2. WHEN ユーザーが Playlist_ID を直接指定した場合、THE CLI SHALL 追加の表示を行わずに従来通り再生を開始する

### Requirement 5: 引数のヘルプ表示の更新

**User Story:** ユーザーとして、`ytm play --help` でプレイリスト名も使えることを知りたい。

#### Acceptance Criteria (受け入れ基準)

1. THE CLI SHALL `play` サブコマンドの引数ヘルプに、Playlist_ID だけでなくプレイリスト名（Shell_Varname 形式または元タイトル）も受け付ける旨を記載する
