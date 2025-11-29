# How-to Guides

実際にコントローラーを動かすためのセットアップ、Open vSwitch との接続、テストの実行手順をまとめています。

## 1. セットアップ
- 前提: Python 3.12+。依存ライブラリは標準ライブラリのみ。
- （統合/パケットテストを実行する場合）Docker と Docker Compose が必要。
- リポジトリを取得:

```bash
git clone https://github.com/yourusername/minisdn-controller.git
cd minisdn-controller
```

## 2. コントローラーの起動
シンプルに Python で起動できます。デフォルトで `0.0.0.0:6634` を待ち受けます。

```bash
python -m src.main
```

起動後のログ例:
```text
[*] Listening on 0.0.0.0 6634
```

## 3. Open vSwitch と接続する
例として `globocom/openvswitch` コンテナを使います。

```bash
# OVS コンテナを起動
docker run --privileged --platform=linux/amd64 -it globocom/openvswitch

# コンテナ内でブリッジをコントローラーに接続
ovs-vsctl set-controller br0 tcp:<YOUR_CONTROLLER_IP>:6634

# 状態確認
ovs-vsctl show

# ovs-vswitchd を起動（まだなら）
/usr/sbin/ovs-vswitchd --detach
```

## 4. テストの実行
`Makefile` にテスト用ターゲットを用意しています。統合系は Docker 必須です。

```bash
# すべてのテスト（ユニット + 統合 + パケットキャプチャ）
make test

# ユニットテストのみ
make test-unit

# 統合テスト（OVS とハンドシェイク確認）
make test-integration

# パケットキャプチャテスト（tcpdump で OpenFlow メッセージを検証）
make test-packets

# 手動確認用（コンテナを残したままログ/通信を確認）
make test-manual
```

### テスト実行の詳細
- ユニットテストを直接走らせたい場合:
  - `python -m unittest discover tests/unit`
  - あるいは `uv run python -m unittest discover tests/unit`
- パケットキャプチャテストでは、`tests/integration/capture.pcap` にキャプチャを保存します。Wireshark 等で確認できます:

```bash
wireshark tests/integration/capture.pcap
```

## 5. トラブルシュート
- Docker 関連で詰まった場合は、コンテナとネットワークをクリーンアップ:

```bash
make clean
# もしくは
cd tests/integration && docker-compose down -v
```
- ポート 6634 が使用中の場合は、競合プロセスを停止するか、`src/controller.py` のポートを変更してください。
- `make test-manual` で立ち上げたコンテナは自動で停止しません。不要になったら `cd tests/integration && docker-compose down -v` で後片付けしてください。

## 6. 手動確認で OVS 側のメッセージを観察する
`make test-manual` でコンテナを残したまま、OVS からコントローラーへどんな OpenFlow メッセージが送られているかを確認できます。

- OVS からコントローラーへの OpenFlow メッセージをライブで見る:

```bash
docker exec -it minisdn-ovs ovs-ofctl monitor br0
```

- 現在のポート/ブリッジ状態を確認:

```bash
docker exec minisdn-ovs ovs-vsctl show
docker exec minisdn-ovs ovs-ofctl show br0
```

- コンテナに入って対話的に確認する:

```bash
docker exec -it minisdn-ovs bash
# 以降コンテナ内で:
ovs-vsctl show
ovs-ofctl show br0
ovs-ofctl dump-flows br0
ovs-ofctl monitor br0   # OpenFlow メッセージのストリームを確認
tail -f /var/log/openvswitch/ovs-vswitchd.log  # ログを直接確認
```

- コントローラー側でパケットを覗く（参考: tcpdump は controller コンテナにインストール済み）:

```bash
docker exec -it minisdn-controller tcpdump -i any port 6634 -vv
```

観察が終わったら、必要に応じて `docker logs -f minisdn-controller` でログも追跡し、終了後に `cd tests/integration && docker-compose down -v` でクリーンアップしてください。
