# minisdn-controller

`minisdn-controller` は Python で書かれたシンプルな OpenFlow 1.0 コントローラーです。学習や検証用途で、Hello/Features のハンドシェイクなど最小限のプロトコルを理解しやすく実装しています。

詳細ドキュメントは `docs/index.md` を参照してください。

## 特徴

- **軽量**: 外部ライブラリに依存せず、標準ライブラリのみで動作します。
- **シンプル**: OpenFlow プロトコルの基本的な動作（接続確立、メッセージ送受信）を理解しやすいコードで実装しています。
- **OpenFlow 対応**: 現在は OpenFlow 1.0 (0x01) の Hello メッセージに対応しています。

## 必要要件

- Python 3.12 以上
- Docker & Docker Compose（統合テスト実行時のみ必要）

## クイックスタート

リポジトリを取得してコントローラーを起動します。

```bash
git clone https://github.com/yourusername/minisdn-controller.git
cd minisdn-controller
python -m src.main
```

起動すると `0.0.0.0:6634` で OpenFlow スイッチからの接続を待ち受けます。Open vSwitch との接続や Docker を用いたテストの詳細手順は `docs/how-to.md` を参照してください。

## テスト

- ユニットテスト: `make test-unit` または `python -m unittest discover tests/unit`
- 統合テスト: `make test-integration`（Docker 必須）
- パケットキャプチャテスト: `make test-packets`（Docker 必須）
- 手動統合チェック（コンテナを残したままログ/通信確認）: `make test-manual`

詳しい手順は `docs/how-to.md` を参照してください。

## プロジェクト構成

```
.
├── src/
│   ├── main.py           # エントリーポイント
│   ├── controller.py     # コントローラークラス
│   ├── openflow.py       # OpenFlowプロトコル実装
│   └── log.py            # ロギングユーティリティ
├── tests/
│   ├── unit/             # ユニットテスト
│   │   ├── test_controller.py
│   │   ├── test_openflow.py
│   │   └── test_log.py
│   └── integration/      # 統合テスト（Docker使用）
│       ├── docker-compose.yml
│       ├── Dockerfile
│       ├── run_test.sh
│       └── verify_packets.sh
├── Makefile              # テスト実行コマンド
├── pyproject.toml        # プロジェクト設定ファイル
└── README.md             # ドキュメント
```

## 今後の予定

- [ ] Echo Request/Reply の実装
- [ ] Packet-In メッセージの解析
- [ ] Flow-Mod メッセージによるフロー制御の実装
- [ ] 複数スイッチのサポート

## ライセンス

MIT License
