"""
test_ytm.py - ytm モジュールのプロパティベーステスト・ユニットテスト

プレイリスト名によるプレイリスト ID 解決機能のテストファイル。
"""

import sys
import urllib.error

import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st
from unittest.mock import patch, MagicMock

from ytm import cli as _ytm
from ytm.cli import (
    resolve_playlist_id,
    to_shell_varname,
    _print_resolved,
    _print_no_match_error,
)


# ---------------------------------------------------------------------------
# Property 1: PL プレフィックス文字列のパススルー
# ---------------------------------------------------------------------------

# PBT: Feature: playlist-name-play, Property 1: PL プレフィックス文字列のパススルー
# **Validates: Requirements 1.1, 4.2**
@given(suffix=st.text())
@settings(max_examples=100)
def test_property1_pl_prefix_passthrough(suffix):
    """PL で始まる文字列はそのまま返され、API 呼び出しは行われない。"""
    pl_string = "PL" + suffix
    with patch.object(_ytm, "fetch_all_playlists") as mock_fetch:
        result = resolve_playlist_id(pl_string)
        assert result == pl_string
        mock_fetch.assert_not_called()


# ---------------------------------------------------------------------------
# Property 2: Shell_Varname による解決
# ---------------------------------------------------------------------------

# PBT: Feature: playlist-name-play, Property 2: Shell_Varname による解決
# **Validates: Requirements 1.3, 4.1**


def playlist_strategy():
    """プレイリスト辞書を生成するストラテジー"""
    return st.fixed_dictionaries({
        "title": st.text(min_size=1, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
        "id": st.text(min_size=3, alphabet=st.characters(whitelist_categories=("L", "N"))).map(lambda s: "PL" + s),
    })


@given(
    playlists=st.lists(playlist_strategy(), min_size=1, max_size=20),
    data=st.data(),
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_property2_shell_varname_resolution(playlists, data):
    """Shell_Varname で検索すると正しいプレイリスト ID が返る。"""
    index = data.draw(st.integers(min_value=0, max_value=len(playlists) - 1))
    chosen = playlists[index]

    varname = to_shell_varname(chosen["title"])

    assume(varname != "")
    assume(not varname.startswith("PL"))

    expected_id = None
    for pl in playlists:
        if to_shell_varname(pl["title"]) == varname:
            expected_id = pl["id"]
            break

    with patch.object(_ytm, "get_api_key", return_value="fake_key"), \
         patch.object(_ytm, "get_channel_id", return_value="fake_channel"), \
         patch.object(_ytm, "fetch_all_playlists", return_value=playlists):
        result = resolve_playlist_id(varname)

    assert result == expected_id


# ---------------------------------------------------------------------------
# Property 3: 元タイトルの大文字小文字無視による解決
# ---------------------------------------------------------------------------

# PBT: Feature: playlist-name-play, Property 3: 元タイトルの大文字小文字無視による解決
# **Validates: Requirements 1.4, 4.1**


def randomize_case(s, data):
    """文字列の各文字の大文字小文字をランダムに変更する"""
    return "".join(
        c.upper() if data.draw(st.booleans()) else c.lower()
        for c in s
    )


def _ascii_playlist_strategy():
    """ASCII 文字のみのプレイリスト辞書を生成するストラテジー。"""
    return st.fixed_dictionaries({
        "title": st.text(
            min_size=1,
            alphabet=st.sampled_from(
                "abcdefghijklmnopqrstuvwxyz"
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                "0123456789 "
            ),
        ),
        "id": st.text(min_size=3, alphabet=st.characters(whitelist_categories=("L", "N"))).map(lambda s: "PL" + s),
    })


@given(
    playlists=st.lists(_ascii_playlist_strategy(), min_size=1, max_size=20),
    data=st.data(),
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_property3_case_insensitive_title_resolution(playlists, data):
    """元タイトルの大文字小文字を変更して検索しても正しいプレイリスト ID が返る。"""
    index = data.draw(st.integers(min_value=0, max_value=len(playlists) - 1))
    chosen = playlists[index]

    search_title = randomize_case(chosen["title"], data)

    assume(not search_title.startswith("PL"))

    all_varnames = {to_shell_varname(pl["title"]) for pl in playlists}
    assume(search_title not in all_varnames)

    search_lower = search_title.lower()
    expected_id = None
    for pl in playlists:
        if pl["title"].lower() == search_lower:
            expected_id = pl["id"]
            break

    with patch.object(_ytm, "get_api_key", return_value="fake_key"), \
         patch.object(_ytm, "get_channel_id", return_value="fake_channel"), \
         patch.object(_ytm, "fetch_all_playlists", return_value=playlists):
        result = resolve_playlist_id(search_title)

    assert result == expected_id


# ---------------------------------------------------------------------------
# Property 4: 一致なしエラー
# ---------------------------------------------------------------------------

# PBT: Feature: playlist-name-play, Property 4: 一致なしエラー
# **Validates: Requirements 1.5**


@given(
    playlists=st.lists(playlist_strategy(), min_size=0, max_size=20),
    search_string=st.text(min_size=1),
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_property4_no_match_error(playlists, search_string):
    """どのプレイリストにも一致しない文字列に対して sys.exit(1) が呼ばれる。"""
    assume(not search_string.startswith("PL"))

    all_varnames = {to_shell_varname(pl["title"]) for pl in playlists}
    assume(search_string not in all_varnames)

    all_titles_lower = {pl["title"].lower() for pl in playlists}
    assume(search_string.lower() not in all_titles_lower)

    with patch.object(_ytm, "get_api_key", return_value="fake_key"), \
         patch.object(_ytm, "get_channel_id", return_value="fake_channel"), \
         patch.object(_ytm, "fetch_all_playlists", return_value=playlists):
        with pytest.raises(SystemExit) as exc_info:
            resolve_playlist_id(search_string)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# Property 5: 解決の優先順位
# ---------------------------------------------------------------------------

# PBT: Feature: playlist-name-play, Property 5: 解決の優先順位
# **Validates: Requirements 2.1, 2.2**


@given(data=st.data())
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_property5_resolution_priority(data):
    """Shell_Varname と元タイトルの両方に一致する場合、Shell_Varname が優先される。"""
    title_a = data.draw(
        st.text(
            min_size=1,
            alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789 "),
        )
    )
    varname_a = to_shell_varname(title_a)
    assume(varname_a != "")
    assume(not varname_a.startswith("PL"))

    id_a = "PL_varname_" + data.draw(
        st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("L", "N")))
    )
    id_b = "PL_title_" + data.draw(
        st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("L", "N")))
    )
    assume(id_a != id_b)

    playlist_a = {"title": title_a, "id": id_a}
    playlist_b = {"title": varname_a, "id": id_b}

    playlists = [playlist_a, playlist_b]

    with patch.object(_ytm, "get_api_key", return_value="fake_key"), \
         patch.object(_ytm, "get_channel_id", return_value="fake_channel"), \
         patch.object(_ytm, "fetch_all_playlists", return_value=playlists):
        result = resolve_playlist_id(varname_a)

    assert result == id_a


# ---------------------------------------------------------------------------
# ユニットテスト: API エラー時の終了
# ---------------------------------------------------------------------------


def test_api_error_exits():
    """API エラー（HTTPError）発生時に sys.exit(1) で終了する。"""
    http_error = urllib.error.HTTPError(
        url="https://example.com",
        code=403,
        msg="Forbidden",
        hdrs={},
        fp=None,
    )
    with patch.object(_ytm, "get_api_key", return_value="fake_key"), \
         patch.object(_ytm, "get_channel_id", return_value="fake_channel"), \
         patch.object(_ytm.urllib.request, "urlopen", side_effect=http_error):
        with pytest.raises(SystemExit) as exc_info:
            resolve_playlist_id("some_name")
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# ユニットテスト: ネットワークエラー時の終了
# ---------------------------------------------------------------------------


def test_network_error_exits():
    """ネットワークエラー（URLError）発生時に sys.exit(1) で終了する。"""
    url_error = urllib.error.URLError(reason="Name or service not known")
    with patch.object(_ytm, "get_api_key", return_value="fake_key"), \
         patch.object(_ytm, "get_channel_id", return_value="fake_channel"), \
         patch.object(_ytm.urllib.request, "urlopen", side_effect=url_error):
        with pytest.raises(SystemExit) as exc_info:
            resolve_playlist_id("some_name")
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# ユニットテスト: ヘルプ文の更新確認
# ---------------------------------------------------------------------------


def test_help_text_mentions_playlist_name():
    """play サブコマンドのヘルプにプレイリスト名の記述が含まれる。"""
    import subprocess as sp
    result = sp.run(
        ["python3", "-m", "ytm.cli", "play", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "プレイリスト名" in result.stdout or \
           "Shell_Varname" in result.stdout or \
           "元タイトル" in result.stdout
