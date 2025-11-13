# SQL TSV Conversion Test Data

このディレクトリには、実際のSQL開発現場で使用される変換パターンのテストデータが含まれています。

## ファイル概要

### TSV変換ルールファイル

#### 1. `schema_conversion.tsv` (35ルール)
環境間のスキーマ変換用TSVファイル。

**変換パターン:**
- `LIVE_USR.*` → `STG_USR.*` (本番→ステージング)
- `PROD_USR.*` → `DEV_USR.*` (本番→開発)
- `PROD_APP.*` → `TEST_APP.*` (本番アプリ→テスト)
- `PROD_DWH.*` → `DEV_DWH.*` (本番DWH→開発DWH)
- `PROD_FINANCE.*` → `TEST_FINANCE.*` (本番財務→テスト)
- `PROD_HR.*` → `DEV_HR.*` (本番人事→開発)

**使用例:**
```sql
-- 変換前
SELECT * FROM LIVE_USR.TABLE1;
SELECT * FROM PROD_USR.SALES;

-- 変換後
SELECT * FROM STG_USR.TABLE1;
SELECT * FROM DEV_USR.SALES;
```

#### 2. `table_conversion.tsv` (20ルール)
テーブル名の変換用TSVファイル。

**変換パターン:**
- `TABLE1` → `TABLE9` (テーブル番号変更)
- `OLD_*` → `NEW_*` (旧→新)
- `LEGACY_*` → `CURRENT_*` (レガシー→現行)
- `*_V1` → `*_V2` (バージョンアップ)
- `BACKUP_2023` → `BACKUP_2024` (年度更新)

**使用例:**
```sql
-- 変換前
SELECT * FROM DEV_USR.TABLE1;
UPDATE DEV_USR.OLD_CUSTOMERS SET status = 'ACTIVE';
SELECT * FROM TEST_APP.TBL_USER_V1;

-- 変換後
SELECT * FROM DEV_USR.TABLE9;
UPDATE DEV_USR.NEW_CUSTOMERS SET status = 'ACTIVE';
SELECT * FROM TEST_APP.TBL_USER_V2;
```

#### 3. `comprehensive_sql_conversion.tsv` (55ルール)
包括的なSQL変換用TSVファイル。スキーマ、テーブル、ストアドプロシージャ、ファンクション、ビュー、インデックスなど、すべての変換パターンを含みます。

**変換パターン:**
- **スキーマ変換** (25ルール): 環境間のスキーマ変換
- **テーブル変換** (10ルール): テーブル名の変更
- **ストアドプロシージャ** (5ルール): `SP_*` の変換
- **ファンクション** (5ルール): `FN_*` の変換
- **ビュー** (5ルール): `VW_*` の変換
- **インデックス** (5ルール): `IDX_*` の変換

**使用例:**
```sql
-- 変換前
SELECT * FROM LIVE_USR.CUSTOMERS;
EXEC SP_GET_CUSTOMER_DATA @customer_id = 12345;
SELECT FN_CALCULATE_TAX(price, tax_rate) FROM PROD_USR.SALES;
SELECT * FROM VW_CUSTOMER_ORDERS;
CREATE INDEX IDX_CUSTOMER_ID ON LIVE_USR.CUSTOMERS(customer_id);

-- 変換後
SELECT * FROM STG_USR.CUSTOMERS;
EXEC SP_RETRIEVE_CUSTOMER_INFO @customer_id = 12345;
SELECT FN_COMPUTE_TAX(price, tax_rate) FROM DEV_USR.SALES;
SELECT * FROM VW_CLIENT_ORDERS;
CREATE INDEX IDX_CLIENT_ID ON STG_USR.CUSTOMERS(customer_id);
```

### SQLテストスクリプト

#### `sample_sql_script.sql`
実際のSQL開発現場で使用される様々なSQLパターンを含むサンプルスクリプト。

**含まれるパターン:**
- 基本的なSELECT、INSERT、UPDATE、DELETE
- JOIN操作（INNER、LEFT、CROSS）
- サブクエリ
- CTE (Common Table Expression)
- ストアドプロシージャ呼び出し
- ファンクション呼び出し
- ビュー参照
- インデックス作成
- トランザクション
- ウィンドウ関数
- MERGE文
- 一時テーブル操作

## 使用方法

### コマンドラインでの使用

```bash
# スキーマ変換
PYTHONPATH=. uv run python main.py transform "/tsv test/performance/sql_test_data/schema_conversion.tsv" \
  --text "$(cat test/performance/sql_test_data/sample_sql_script.sql)" \
  --no-clipboard

# テーブル名変換
PYTHONPATH=. uv run python main.py transform "/tsv test/performance/sql_test_data/table_conversion.tsv" \
  --text "$(cat your_sql_file.sql)" \
  --no-clipboard

# 包括的変換
PYTHONPATH=. uv run python main.py transform "/tsv test/performance/sql_test_data/comprehensive_sql_conversion.tsv" \
  --text "$(cat your_sql_file.sql)" \
  --no-clipboard
```

### Pythonコードでの使用

```python
from text_core.transformers.string_transformer import StringTransformer

# SQLスクリプトを読み込み
with open("your_sql_script.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

# 変換実行
transformer = StringTransformer()
result = transformer._tsv_replacements(
    sql_script,
    ["test/performance/sql_test_data/schema_conversion.tsv"]
)

# 結果を保存
with open("converted_sql_script.sql", "w", encoding="utf-8") as f:
    f.write(result)
```

### 大小文字区別オプション

```bash
# 大小文字を区別しない（デフォルト）
PYTHONPATH=. uv run python main.py transform "/tsv schema_conversion.tsv" --text "..."

# 大小文字を区別する
PYTHONPATH=. uv run python main.py transform "/tsv schema_conversion.tsv -c" --text "..."
```

## テスト実行

```bash
# すべてのSQLテストを実行
cd test/performance
PYTHONPATH=. uv run pytest test_sql_tsv_conversion.py -v -s

# 個別テストを実行
PYTHONPATH=. uv run pytest test_sql_tsv_conversion.py::TestSQLTSVConversion::test_schema_conversion_live_to_stg -v -s
```

## パフォーマンス結果

### テスト環境
- Python 3.13.7
- Windows環境
- 入力サイズ: 6,699文字（201行）

### 結果サマリー

| テストタイプ | ルール数 | 処理時間 | メモリ使用量 | スループット |
|------------|----------|---------|-------------|------------|
| スキーマ変換 | 35 | 0.002秒 | 0.04 MB | 3,730,371 chars/sec |
| テーブル変換 | 20 | 0.001秒 | 0.04 MB | 5,309,924 chars/sec |
| 包括的変換 | 55 | 0.003秒 | 0.04 MB | 2,149,734 chars/sec |

### 検証結果

#### TEST 1: スキーマ変換
- **検証済み変換**: 7件
- 主要変換:
  - `LIVE_USR.TABLE1` → `STG_USR.TABLE1`
  - `PROD_USR.SALES` → `DEV_USR.SALES`
  - `PROD_APP.USER_DATA` → `TEST_APP.USER_DATA`

#### TEST 2: テーブル名変換
- **検証済み変換**: 5件
- 主要変換:
  - `DEV_USR.TABLE1` → `DEV_USR.TABLE9`
  - `DEV_USR.OLD_CUSTOMERS` → `DEV_USR.NEW_CUSTOMERS`
  - `TEST_APP.TBL_USER_V1` → `TEST_APP.TBL_USER_V2`

#### TEST 3: 包括的変換
- **検証済み変換**: 14件
- カテゴリ別:
  - スキーマ変換: 3件
  - テーブル変換: 2件
  - ストアドプロシージャ: 3件
  - ファンクション: 2件
  - ビュー: 2件
  - インデックス: 2件

## 実際のユースケース

### ユースケース1: 本番からステージング環境へのSQL移行

```bash
# 本番環境のSQLスクリプトをステージング環境用に変換
PYTHONPATH=. uv run python main.py transform \
  "/tsv test/performance/sql_test_data/schema_conversion.tsv" \
  --text "$(cat production_script.sql)" \
  > staging_script.sql
```

### ユースケース2: テーブルリネーム後のSQLスクリプト更新

```bash
# テーブル名変更後、既存のSQLスクリプトを一括更新
PYTHONPATH=. uv run python main.py transform \
  "/tsv test/performance/sql_test_data/table_conversion.tsv" \
  --text "$(cat old_queries.sql)" \
  > updated_queries.sql
```

### ユースケース3: 複数の変換を順次適用

```bash
# 1. スキーマ変換
cat original.sql | \
  PYTHONPATH=. uv run python main.py transform \
    "/tsv schema_conversion.tsv" --text - > temp1.sql

# 2. テーブル名変換
cat temp1.sql | \
  PYTHONPATH=. uv run python main.py transform \
    "/tsv table_conversion.tsv" --text - > final.sql
```

## カスタムTSVファイルの作成

### TSVファイルフォーマット

```
old_pattern<TAB>new_pattern
```

### 作成例

```tsv
PROD_SCHEMA.TABLE1	DEV_SCHEMA.TABLE1
PROD_SCHEMA.TABLE2	DEV_SCHEMA.TABLE2
OLD_PROCEDURE_NAME	NEW_PROCEDURE_NAME
old_column	new_column
```

### ベストプラクティス

1. **具体的なパターンを優先**: `PROD_USR.CUSTOMERS` よりも `PROD_USR.CUSTOMER_MASTER` のような具体的な名前を先に記載
2. **順序を考慮**: より長いパターンを先に記載して部分一致を防ぐ
3. **テスト**: 少数のルールでテストしてから本番適用
4. **バックアップ**: 変換前に元のSQLファイルをバックアップ

## トラブルシューティング

### 問題: 一部の変換が適用されない

**原因**: パターンの順序や部分一致の問題

**解決策**:
- より具体的で長いパターンをTSVファイルの上部に配置
- 大小文字の区別が必要な場合は `-c` フラグを使用

### 問題: 意図しない箇所が変換される

**原因**: パターンが広範囲すぎる

**解決策**:
- より具体的なパターンを使用（例: `TABLE1` ではなく `SCHEMA.TABLE1`）
- 正規表現モード（`-r`）でワード境界を使用

## 関連ファイル

- テストスクリプト: `test/performance/test_sql_tsv_conversion.py`
- パフォーマンステスト: `test/performance/test_tsv_performance.py`
- 変換エンジン: `components/text_core/transformers/string_transformer.py`

## ライセンス

MIT License
