# minisdn-controller

`minisdn-controller` は、Python で書かれたシンプルな OpenFlow コントローラーです。
学習用やテスト用として、最小限の OpenFlow プロトコル（現在は Hello メッセージのハンドシェイクなど）を実装することを目的としています。

## 特徴

- **軽量**: 外部ライブラリに依存せず、標準ライブラリのみで動作します。
- **シンプル**: OpenFlow プロトコルの基本的な動作（接続確立、メッセージ送受信）を理解しやすいコードで実装しています。
- **OpenFlow 対応**: 現在は OpenFlow 1.0 (0x01) の Hello メッセージに対応しています。

## 必要要件

- Python 3.12 以上

## インストール

このリポジトリをクローンしてください。

```bash
git clone https://github.com/yourusername/minisdn-controller.git
cd minisdn-controller
```

依存関係の管理には `uv` や標準の `pip` が利用可能ですが、現在は外部依存ライブラリはありません。

## 使い方

コントローラーを起動します。

```bash
python main.py
```

起動すると、デフォルトで `0.0.0.0:6634` で OpenFlow スイッチからの接続を待ち受けます。

```text
[*]Listening on 0.0.0.0 6634
```

OpenFlow スイッチ（Mininet や Open vSwitch など）から接続があると、Hello メッセージを送信し、スイッチからのメッセージを受信して表示します。

## プロジェクト構成

```
.
├── main.py           # エントリーポイント。ソケット通信とOpenFlowハンドシェイクのロジック
├── pyproject.toml    # プロジェクト設定ファイル
└── README.md         # ドキュメント
```

## 今後の予定

- [ ] Echo Request/Reply の実装
- [ ] Packet-In メッセージの解析
- [ ] Flow-Mod メッセージによるフロー制御の実装
- [ ] 複数スイッチのサポート

## ライセンス

MIT License
