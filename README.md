# Simple Table Calculator

シンプルで軽量な表計算Webアプリケーション。Excelライクな操作感で、列間の自動計算機能を提供します。

## 🚀 クイックスタート

```bash
# 依存関係のインストール
uv sync

# サーバー起動
uv run uvicorn main:app --reload

# ブラウザでアクセス
http://localhost:8000
```

## ✨ 主な機能

### 自動計算機能
- **Param列**: 計算で使用する係数（float）を入力
- **A列**: 基準値（base value）を入力
- **B列**: A + Param を自動計算・表示
- **C列**: A × Param を自動計算・表示

どの列に入力しても、他の列が自動的に計算・更新されます：
- A列入力時 → B, C列を自動計算
- B列入力時 → A = B - Param, C = A × Param
- C列入力時 → A = C ÷ Param, B = A + Param

### 操作性
- **Excelライクな操作感**
  - フォーカスモード（緑枠）: 矢印キーでセル移動
  - 編集モード（水色背景）: 直接入力
  - Tab/Shift+Tab: 次/前のセルへ移動
  - Enter: 下のセルへ移動（編集確定）
  - Esc: 編集をキャンセル
  - F2またはEnter: 編集モード開始
  - 文字入力: セル内容をクリアして新規入力

### データ管理
- **行の追加**: ボタンクリックで新規行を追加
- **ソート機能**: 列ヘッダークリックで昇順/降順ソート
- **ドラッグ&ドロップ**:
  - 行の並び替え: 行全体をドラッグして順序変更
  - 列の並び替え: 列ヘッダーをドラッグして順序変更
- **CSVエクスポート**: 現在の表データをCSVファイルとしてダウンロード
- **Param補完**: datalistによる入力候補表示（0.5, 1.0, 1.5, 2.0, 10, 100）

### セッション管理
- **独立したセッション**: 各ユーザーが独自のデータ空間を持つ
- **セッション共有**: URLパラメータ（`?session=xxx`）でセッションを共有可能
- **自動クリーンアップ**: 1時間アクセスがないセッションは自動削除
- **リアルタイム同期**: WebSocketによる同一セッション内でのリアルタイム更新

## 🛠️ 技術仕様

### アーキテクチャ
- **バックエンド**: FastAPI + WebSocket（main.py - 約190行）
- **フロントエンド**: 素のHTML/CSS/JavaScript（index.html - 約615行）
- **データストア**: インメモリ（セッションごとに分離）
- **依存関係**: 最小限（FastAPI, uvicorn[standard]のみ）

### ファイル構成
```
simple-table-calculator/
├── main.py              # FastAPIアプリケーション
├── static/
│   └── index.html      # UI（全フロントエンドコード含む）
├── README.md
└── pyproject.toml
```

### パフォーマンス
- 初期ロード: 100ms以下
- セル更新: 50ms以下でリアルタイム反映
- 1000行まで快適に動作
- メモリ使用量: セッションあたり50MB以下

---

## 📐 設計（実装時の設計ドキュメント）

### アーキテクチャ
最小限のシンプルな構成：
- **バックエンド**: FastAPI（単一ファイル）
- **フロントエンド**: 素のHTML/CSS/JavaScript（フレームワークなし）
- **データ**: インメモリ（DBなし）

### ディレクトリ構造
```
simple-table-calculator/
├── main.py           # FastAPIアプリ（全バックエンドロジック）
├── static/
│   └── index.html    # UI（HTML/CSS/JS全て含む）
├── README.md
└── pyproject.toml
```

### 実装計画

#### Phase 1: 基本機能（1日目）✅
1. **FastAPIセットアップ**
   - 静的ファイル配信
   - WebSocket接続（リアルタイム更新用）
   - データ構造定義（行のリスト）

2. **基本的な表UI**
   - HTML table要素で表を表示
   - contenteditable属性でセル編集
   - Tab/Enterキーナビゲーション

3. **計算ロジック**
   - param入力時：そのまま保存
   - A列入力時：B = A + param, C = A * param
   - B列入力時：A = B - param, C = A * param
   - C列入力時：A = C / param, B = A + param

#### Phase 2: 追加機能（2日目）✅
1. **行の追加**
   - 「+」ボタンで新規行追加
   - 自動的に番号付け

2. **param補完**
   - datalist要素で候補表示
   - 設定から候補リスト管理

3. **WebSocketでリアルタイム同期**
   - セル変更時に即座に計算・表示更新
   - 同一セッション内での同期

#### 追加実装機能
1. **セッション分離**
   - 各ユーザーが独立したデータ空間
   - URLパラメータでセッション共有可能

2. **高度な操作機能**
   - 列のソート（クリックで昇順/降順）
   - 行のドラッグ&ドロップ並び替え
   - 列のドラッグ&ドロップ並び替え
   - CSVダウンロード機能

3. **UI/UX改善**
   - フォーカス/編集モードの分離
   - Escキーで編集キャンセル
   - 矢印キーでのナビゲーション

### 技術詳細

#### データモデル（Python）
```python
class Row:
    id: int
    param: float | None
    a: float | None
    b: float | None
    c: float | None
```

#### API設計
- `GET /` - 静的ファイル配信
- `WebSocket /ws` - リアルタイム通信
  - 受信: `{"action": "update", "row_id": 1, "column": "a", "value": 100}`
  - 送信: `{"rows": [...]}`

#### フロントエンド
- 純粋なDOM操作（jQuery不要）
- WebSocket接続管理
- キーボードイベント処理
- 200行以下のコンパクトな実装

### 依存関係（最小限）
```toml
dependencies = [
    "fastapi",
    "uvicorn[standard]",  # WebSocket対応
]
```

### 開発・実行
```bash
# 依存関係インストール
uv add fastapi "uvicorn[standard]"

# 開発サーバー起動
uv run uvicorn main:app --reload

# ブラウザでアクセス
# http://localhost:8000
```

### パフォーマンス目標
- 初期ロード: 100ms以下
- セル更新反映: 50ms以下
- 1000行まで快適に動作
- メモリ使用量: 50MB以下