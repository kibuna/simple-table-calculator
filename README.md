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

---

## 🔄 より保守性の高い実装案

現在の実装は簡潔さを重視していますが、より大規模な開発やメンテナンスを考慮した場合、以下のような構成が考えられます：

### フロントエンド構成案

#### 1. React + TypeScript構成
```
frontend/
├── src/
│   ├── components/
│   │   ├── Table/
│   │   │   ├── Table.tsx
│   │   │   ├── Cell.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Row.tsx
│   │   ├── Controls/
│   │   │   ├── AddRowButton.tsx
│   │   │   └── ExportButton.tsx
│   │   └── Layout/
│   │       └── AppLayout.tsx
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   ├── useTableData.ts
│   │   └── useKeyboardNavigation.ts
│   ├── services/
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── types/
│   │   └── table.ts
│   └── utils/
│       ├── calculations.ts
│       └── csv.ts
├── package.json
└── tsconfig.json
```

**メリット:**
- コンポーネントの再利用性
- 型安全性（TypeScript）
- 状態管理の明確化（React Hooks）
- テストしやすい構造

#### 2. Vue 3 + Composition API構成
```
frontend/
├── src/
│   ├── components/
│   │   ├── TableView.vue
│   │   ├── TableCell.vue
│   │   └── ControlPanel.vue
│   ├── composables/
│   │   ├── useTable.ts
│   │   ├── useWebSocket.ts
│   │   └── useDragDrop.ts
│   ├── stores/
│   │   └── tableStore.ts (Pinia)
│   └── types/
│       └── index.ts
```

### バックエンド構成案

#### 1. FastAPI + Clean Architecture
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── table.py
│   │   │   │   └── websocket.py
│   │   │   └── api.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── table.py
│   │   │   └── session.py
│   │   └── value_objects/
│   │       └── cell.py
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   ├── memory.py
│   │   │   └── redis.py
│   │   └── websocket/
│   │       └── connection_manager.py
│   ├── use_cases/
│   │   ├── calculate_cells.py
│   │   ├── export_csv.py
│   │   └── manage_session.py
│   └── main.py
├── tests/
├── alembic/ (将来的なDB移行用)
└── requirements.txt
```

**メリット:**
- ビジネスロジックの分離
- テスタビリティの向上
- 依存性の注入
- 将来的な永続化層の変更が容易

#### 2. データ永続化オプション
- **Redis**: セッションデータの高速アクセス
- **PostgreSQL + SQLAlchemy**: 永続的なデータ保存
- **MongoDB**: スキーマレスな表データの保存

### インフラ構成案

#### Docker Compose開発環境
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 追加機能の実装しやすさ

上記の構成により、以下の機能追加が容易になります：

1. **認証・認可**
   - JWT認証
   - ユーザーごとの表管理
   - 共有権限の細かい制御

2. **高度な表計算機能**
   - 数式パーサー（より複雑な計算式）
   - カスタム関数の定義
   - 条件付き書式

3. **コラボレーション機能**
   - リアルタイムカーソル表示
   - コメント機能
   - 変更履歴の追跡

4. **データ分析機能**
   - グラフ生成
   - ピボットテーブル
   - データのインポート/エクスポート（Excel対応）

### 段階的な移行戦略

1. **Phase 1**: 現在のコードをリファクタリング
   - ビジネスロジックを関数に分離
   - WebSocket管理をクラス化

2. **Phase 2**: TypeScriptの導入
   - フロントエンドの型定義
   - APIクライアントの生成

3. **Phase 3**: コンポーネント化
   - Reactなどのフレームワーク導入
   - 状態管理の整理

4. **Phase 4**: バックエンドアーキテクチャ改善
   - Clean Architectureの適用
   - 永続化層の追加

この段階的アプローチにより、現在の軽量さを保ちながら、必要に応じてスケーラブルな構成に移行できます。