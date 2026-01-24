# 環境構築ガイド

Voice Clone ツールの環境構築手順を説明します。

## 前提条件

- Windows 10/11 + WSL2
- WSLg が有効（Windows 11 または Windows 10 21H2以降）
- Python 3.10 以上
- 16GB RAM 推奨

## 1. WSL2 の確認

PowerShell で WSL のバージョンを確認します。

```powershell
wsl --version
```

WSLg が有効かどうかは、WSL 内で以下を確認します。

```bash
ls /mnt/wslg
```

`/mnt/wslg` ディレクトリが存在すれば WSLg が有効です。

## 2. 必要なシステムパッケージのインストール

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    pulseaudio \
    pulseaudio-utils \
    alsa-utils \
    libportaudio2
```

## 3. WSLg オーディオ設定

プロジェクトに含まれるセットアップスクリプトを実行します。

```bash
cd voice-clone
./setup_wslg.sh
```

このスクリプトは以下を行います：

1. 必要なオーディオパッケージのインストール
2. `~/.asoundrc` の設定（ALSA → PulseAudio ルーティング）
3. `PULSE_SERVER` 環境変数の設定
4. オーディオデバイスの確認

### 手動設定（スクリプトが動作しない場合）

#### ~/.asoundrc の作成

```bash
cat > ~/.asoundrc << 'EOF'
pcm.!default {
    type pulse
}
ctl.!default {
    type pulse
}
EOF
```

#### 環境変数の設定

`~/.bashrc` に追加：

```bash
export PULSE_SERVER="unix:/mnt/wslg/PulseServer"
```

設定を反映：

```bash
source ~/.bashrc
```

## 4. Python 仮想環境の作成

```bash
cd voice-clone

# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# パッケージのインストール
pip install -e .
```

インストールされる主要パッケージ：

| パッケージ | 用途 |
|-----------|------|
| click | CLI フレームワーク |
| sounddevice | オーディオ録音 |
| soundfile | オーディオファイル読み書き |
| torch | 深層学習フレームワーク |
| transformers | Hugging Face モデル |
| rich | CLI 出力の装飾 |

## 5. インストールの確認

```bash
# CLI が動作するか確認
voice-clone --version

# オーディオデバイスの確認
voice-clone devices --audio

# GPU 情報の確認（CPU のみの場合は "CUDA Available: No"）
voice-clone devices --gpu
```

## 6. マイクの確認

### Windows 側の設定

1. Windows 設定 → プライバシーとセキュリティ → マイク
2. 「マイクへのアクセス」を オン
3. 「アプリがマイクにアクセスできるようにする」を オン

### WSL 側の確認

```bash
# PulseAudio ソースの確認
pactl list sources short
```

`RDPSource` または類似の名前が表示されれば、Windows のマイクにアクセス可能です。

## トラブルシューティング

### マイクが認識されない

1. Windows のマイク設定を確認
2. WSL を再起動

```powershell
# PowerShell から実行
wsl --shutdown
```

3. WSL を再度起動してセットアップスクリプトを再実行

### PulseAudio 接続エラー

```bash
# PulseAudio サーバーの状態確認
pactl info
```

エラーが出る場合は、環境変数を確認：

```bash
echo $PULSE_SERVER
# 出力: unix:/mnt/wslg/PulseServer
```

### pip install でエラーが出る

PyTorch のインストールに時間がかかる場合があります。タイムアウトした場合は再実行してください。

```bash
pip install --timeout 300 -e .
```

## 次のステップ

環境構築が完了したら、[クイックスタートガイド](./quick-start.md) に進んでください。
