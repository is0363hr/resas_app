# RESAS_APP

## 目的

ビックデータを扱って、アプリケーションを開発する、そのノウハウを学習するため。

## システム構成

### 情報収集

地域経済分析システム（RESAS_API）から情報を収集

### データベース

分散処理マルチテナント対応検索エンジンであるElasticsearchを使用

### 可視化ツール

オープンソースのフロントエンドアプリであるKibanaを使用


## 開発環境

| 使用ツール | バージョン | URL |
| ---- | ---- | ---- |
|  Elasticserach  |  6.6.2  | https://www.elastic.co/jp/downloads/past-releases/elasticsearch-6-6-2 |
|  Kibana  |  6.6.2  | https://www.elastic.co/jp/downloads/past-releases/kibana-6-6-2 |
| java | 1.8 | https://www.oracle.com/technetwork/jp/java/javase/downloads/jre8-downloads-2133155.html |
| python(仮想環境) | 3.6 | https://www.anaconda.com/ |

## 使用ライブラリ (Python)
| 使用ライブラリ | 説明 |
| ---- | ---- |
| elasticsearch | ElasticSearchのWrapperライブラリ |
| Flask | Web開発用のフレームワーク |
| Pandas | データフレームのライブラリ |
| Numpy | python用の数値計算Wrapperライブラリ |

## 使用ライブラリ(javascript)

| 使用ライブラリ | 説明 |
| ---- | ---- |
| VEGA | JSONによる描画ライブラリ |
| DataTables | テーブル表示に関するライブラリ |
| Bootstrap | Twitter社が開発したCSSの「フレームワーク」 |
| TypeScript | マイクロソフトが開発した静的型付きのjavascript |


# 参考

Pythonコードのコーディング規約
https://pep8-ja.readthedocs.io/ja/latest/
