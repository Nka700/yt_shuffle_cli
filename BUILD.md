# ビルド手順

## 前提

- Python 3.8+
- `build` パッケージ（`pip install build`）

## パッケージビルド

```bash
python3 -m build
```

`dist/` に以下が生成される:

- `ytm-1.0.0-py3-none-any.whl` — wheel パッケージ
- `ytm-1.0.0.tar.gz` — ソース配布物

## インストール

```bash
# wheel から
pip install dist/ytm-1.0.0-py3-none-any.whl

# 開発用（editable install）
pip install -e .
```

インストール後、`ytm` コマンドが PATH に追加される。

## テスト実行

```bash
pip install pytest hypothesis
python3 -m pytest tests/ -v
```

## ビルド設定

`pyproject.toml` で管理:

| 項目 | 設定 |
|------|------|
| ビルドバックエンド | hatchling |
| ソースコード | `src/ytm/` |
| エントリポイント | `ytm = "ytm.cli:main"` |
| 出力先 | `dist/`（デフォルト） |
