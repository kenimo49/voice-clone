# Voice Clone

Qwen3-TTS を使用した音声クローンツール。WSLg で録音し、任意のテキストを指定した声で読み上げた音声ファイルを生成します。

## 特徴

- 3秒程度の音声サンプルで声をクローン可能
- 日本語を含む多言語対応
- WSLg 録音対応
- CPU でも動作可能（ただし低速）

## 必要環境

- Python 3.10 以上
- WSL2 with WSLg（録音機能を使用する場合）
- 16GB RAM 推奨

## インストール

```bash
# リポジトリのクローン
cd voice-clone

# WSLg オーディオ設定（初回のみ）
./setup_wslg.sh

# 仮想環境の作成とパッケージインストール
python -m venv venv
source venv/bin/activate
pip install -e .
```

## 使い方

### デバイス確認

```bash
# オーディオデバイス一覧
voice-clone devices --audio

# GPU情報
voice-clone devices --gpu

# 両方表示
voice-clone devices
```

### 録音

```bash
# 5秒間録音
voice-clone record -o samples/speaker_a.wav -d 5

# インタラクティブモード（Enter で開始/停止）
voice-clone record -o samples/speaker_a.wav --interactive

# デバイス指定
voice-clone record -o samples/speaker_a.wav -d 5 --device 1
```

### 音声生成

```bash
# 基本的な使い方
voice-clone generate \
  -r samples/speaker_a.wav \
  -t "こんにちは、今日もいい天気ですね" \
  -o outputs/hello.wav

# CPU モードで実行
voice-clone generate \
  -r samples/speaker_a.wav \
  -t "テスト音声です" \
  -o outputs/test.wav \
  --device cpu
```

## ディレクトリ構成

```
voice-clone/
├── README.md
├── CLAUDE.md
├── pyproject.toml
├── setup_wslg.sh
├── src/voice_clone/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── devices.py
│   │   └── recorder.py
│   └── tts/
│       ├── __init__.py
│       └── qwen_tts.py
├── samples/          # 入力音声サンプル
└── outputs/          # 生成音声出力
```

## 技術的メモ

### 使用モデル

- **Qwen/Qwen3-TTS-12Hz-0.6B**: 軽量版、16GB RAM で余裕を持って動作

### CPU 動作について

CPU でも動作しますが、10秒の音声生成に30秒〜1分程度かかります。

### WSLg オーディオ

- PulseAudio 経由で Windows のマイクにアクセス
- `~/.asoundrc` で ALSA から PulseAudio へルーティング
- 環境変数 `PULSE_SERVER` を設定

## トラブルシューティング

### マイクが認識されない

1. Windows 設定 > プライバシー > マイク でアプリのアクセスを許可
2. WSL を再起動: `wsl --shutdown`（PowerShell から）
3. `./setup_wslg.sh` を再実行

### 録音テスト

```bash
# デバイス確認
voice-clone devices --audio

# 短い録音テスト
voice-clone record -o test.wav -d 3

# 再生確認
aplay test.wav
```

## ライセンス

MIT License

## 参考

- [Qwen3-TTS GitHub](https://github.com/QwenLM/Qwen3-TTS)
- [Hugging Face - Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B)
