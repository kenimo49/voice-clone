# CLAUDE.md – Voice Clone プロジェクトガイド

## ⚡ TL;DR - 目的別クイックナビゲーション

目的に応じて以下のセクションへジャンプしてください：

| 目的                       | 参照先                                                            | 所要時間 |
| -------------------------- | ----------------------------------------------------------------- | -------- |
| **ツールを使いたい**       | [docs/guide/quick-start.md](./docs/guide/quick-start.md)          | 5 分     |
| **環境構築**               | [docs/guide/environment-setup.md](./docs/guide/environment-setup.md) | 15 分    |
| **新機能の実装**           | [🏗 プロジェクト構造](#-プロジェクト構造) → 該当モジュール        | 10 分    |
| **バグ修正・デバッグ**     | [🔧 主要コマンド](#-主要コマンド) → [📁 コード構成](#-コード構成) | 10 分    |
| **技術仕様の確認**         | [📚 技術スタック](#-技術スタック)                                 | 5 分     |

### 決定木

```mermaid
graph TD
    Start([CLAUDEに依頼]) --> Task{タスクは？}

    Task -->|使い方を知りたい| Quick[📖 クイックスタート<br/>docs/guide/quick-start.md]
    Task -->|環境を構築したい| Env[🔧 環境構築ガイド<br/>docs/guide/environment-setup.md]
    Task -->|新機能を実装| Impl[実装タスク]
    Task -->|バグを修正| Bug[デバッグタスク]

    Impl --> ImplType{何を実装？}
    ImplType -->|録音関連| Audio[audio/<br/>devices.py, recorder.py]
    ImplType -->|TTS関連| TTS[tts/<br/>qwen_tts.py]
    ImplType -->|CLI拡張| CLI[cli.py]

    Bug --> BugType{何が問題？}
    BugType -->|録音できない| AudioDebug[WSLGオーディオ設定<br/>setup_wslg.sh 確認]
    BugType -->|生成エラー| TTSDebug[モデル・メモリ確認<br/>qwen_tts.py]
    BugType -->|CLI不具合| CLIDebug[cli.py の該当コマンド]

    Quick --> Use([使用開始])
    Env --> Use
    Audio --> Implement([実装開始])
    TTS --> Implement
    CLI --> Implement
    AudioDebug --> Fix([修正開始])
    TTSDebug --> Fix
    CLIDebug --> Fix
```

---

## 🗣 言語設定

- 回答は **基本的に日本語** でお願いします
- ただし、コード中のコメントや技術用語については英語のままで構いません

---

## 📖 概要

Qwen3-TTS を使用した音声クローンプロジェクト。
WSLGで録音し、任意のテキストを指定した声で読み上げた音声ファイルを生成する。

---

## 📚 技術スタック

| カテゴリ         | 技術                                              |
| ---------------- | ------------------------------------------------- |
| 言語             | Python 3.10+                                      |
| TTSモデル        | Qwen3-TTS（0.6B / 1.7B）                          |
| STTモデル        | Vosk（ローカル、無料）                            |
| CLI              | click                                             |
| オーディオ       | sounddevice / soundfile / pydub                   |
| 深層学習         | transformers / torch                              |
| UI装飾           | rich                                              |
| YouTube音声取得  | yt-dlp                                            |

### 動作要件

- **OS**: Windows 10/11 + WSL2（WSLg有効）
- **RAM**: 16GB 推奨
- **GPU**: オプション（CUDAサポート、CPUでも動作可能）

---

## 🏗 プロジェクト構造

```
voice-clone/
├── CLAUDE.md              # このファイル（AI向けガイド）
├── README.md              # プロジェクト説明
├── pyproject.toml         # パッケージ設定
├── setup_wslg.sh          # WSLGオーディオセットアップ
├── docs/
│   └── guide/
│       ├── quick-start.md       # クイックスタート
│       └── environment-setup.md # 環境構築
├── src/voice_clone/
│   ├── __init__.py
│   ├── cli.py             # CLIエントリポイント
│   ├── config.py          # 設定管理
│   ├── audio/
│   │   ├── devices.py     # デバイス管理
│   │   └── recorder.py    # 録音機能
│   ├── tts/
│   │   └── qwen_tts.py    # Qwen3-TTSラッパー
│   └── stt/
│       └── vosk_stt.py    # Vosk音声認識
├── samples/               # 入力音声サンプル
└── outputs/               # 生成音声出力
```

---

## 📁 コード構成

### エントリポイント

- **`src/voice_clone/cli.py`**: CLI コマンド定義（`devices`, `record`, `generate`, `transcribe`, `download-model`）

### 音声処理 (`audio/`)

- **`devices.py`**: オーディオデバイスの列挙・選択
- **`recorder.py`**: マイク録音機能（固定時間/インタラクティブ）

### TTS (`tts/`)

- **`qwen_tts.py`**: Qwen3-TTS モデルのラッパー
  - モデルのロード・キャッシュ
  - 参照音声からの音声合成

### STT (`stt/`)

- **`vosk_stt.py`**: Vosk 音声認識エンジン
  - 音声ファイルからテキストへの変換
  - モデルの自動ダウンロード
  - 日本語/英語/中国語対応

### 設定

- **`config.py`**: デフォルト設定値の管理

---

## 🔧 主要コマンド

```bash
# デバイス確認
voice-clone devices --audio    # オーディオデバイス一覧
voice-clone devices --gpu      # GPU情報

# 録音
voice-clone record -o samples/speaker.wav -d 5           # 5秒録音
voice-clone record -o samples/speaker.wav --interactive  # 手動開始/停止

# 音声生成
voice-clone generate \
  -r samples/speaker.wav \
  -t "読み上げテキスト" \
  -o outputs/output.wav

# 高品質モデル + テンション調整
voice-clone generate \
  -r samples/speaker.wav \
  -t "元気な挨拶！" \
  -o outputs/output.wav \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-Base \
  --temperature 1.3

# 参照テキスト指定で精度向上
voice-clone generate \
  -r samples/speaker.wav \
  --ref-text "参照音声で話している内容" \
  -t "新しく生成するテキスト" \
  -o outputs/output.wav

# 参照音声を自動でテキスト化（Vosk使用）
voice-clone generate \
  -r samples/speaker.wav \
  --auto-transcribe \
  -t "新しく生成するテキスト" \
  -o outputs/output.wav

# 音声ファイルをテキスト化
voice-clone transcribe -i samples/speaker.wav
voice-clone transcribe -i samples/english.wav -l en

# Voskモデルをダウンロード
voice-clone download-model           # 日本語
voice-clone download-model -l en     # 英語
```

---

## 📝 開発メモ

### パフォーマンス

| 環境               | 10秒音声の生成時間 |
| ------------------ | ------------------ |
| CPU（i7-10610U）   | 30秒〜1分          |
| GPU（CUDA）        | 数秒               |

### WSLGオーディオ

- PulseAudio 経由でWindowsマイクにアクセス
- `~/.asoundrc` の設定が必要（`setup_wslg.sh` で自動設定）
- 環境変数: `PULSE_SERVER="unix:/mnt/wslg/PulseServer"`

### モデル

| モデル | サイズ | 推奨環境 |
|--------|--------|----------|
| `Qwen/Qwen3-TTS-12Hz-0.6B-Base` | 0.6B | CPU / GPU |
| `Qwen/Qwen3-TTS-12Hz-1.7B-Base` | 1.7B | GPU（VRAM 8GB+） |

- デフォルト: 0.6B モデル（軽量版）
- `--model` オプションで切り替え可能
- 詳細は [TTS ガイド](./docs/guide/tts.md) 参照

### 音声テンション調整

`--temperature` オプションで音声の抑揚・エネルギーを調整可能：

| temperature | 効果 | 用途 |
|-------------|------|------|
| 0.7〜0.9 | 落ち着いた・安定 | ナレーション、解説 |
| 1.0 | 標準（デフォルト） | 一般的な用途 |
| 1.2〜1.5 | 元気・ハイテンション | キャラボイス、挨拶 |

**Tips**:
- テキストに「！」を多用すると、さらにテンションが上がる
- `--temperature 1.3` + 「！」の組み合わせが効果的
- 詳細は [TTS ガイド](./docs/guide/tts.md) 参照

### 参照テキスト（Knowledge）による再現度向上

参照音声の内容（何を話しているか）をテキストとして提供すると、音声クローンの再現度が向上します。

| モード | 仕組み | 再現度 |
|--------|--------|--------|
| `--ref-text` なし | 音声から話者特徴（x-vector）のみ抽出 | ★★☆ |
| `--auto-transcribe` | 自動認識したテキストを使用 | ★★★ |
| `--ref-text` 手動指定 | 正確なテキストを使用 | ★★★★ |

**なぜ効果的か**: モデルに「この音声でこのテキストを話している」という知識（knowledge）を与えることで、音声とテキストの対応関係を理解し、より正確に話者特徴を学習できます。

**推奨ワークフロー**:
```bash
# 1. 参照音声をテキスト化
voice-clone transcribe -i samples/speaker.wav

# 2. 認識結果を確認・修正（句読点追加など）

# 3. 修正したテキストを ref-text として使用
voice-clone generate \
  -r samples/speaker.wav \
  --ref-text "正確なテキスト" \
  -t "新しいテキスト" \
  -o outputs/output.wav
```

詳細は [音声テキスト化ガイド](./docs/guide/transcription.md) 参照

---

## 📚 ドキュメント

| ドキュメント                                              | 内容                           |
| --------------------------------------------------------- | ------------------------------ |
| [docs/README.md](./docs/README.md)                        | ドキュメントインデックス       |
| [docs/guide/quick-start.md](./docs/guide/quick-start.md)  | ツールの基本的な使い方         |
| [docs/guide/environment-setup.md](./docs/guide/environment-setup.md) | 環境構築の詳細手順 |
| [docs/guide/recording.md](./docs/guide/recording.md)      | マイクでの録音方法             |
| [docs/guide/youtube-audio.md](./docs/guide/youtube-audio.md) | YouTube からの音声抽出      |
| [docs/guide/tts.md](./docs/guide/tts.md)                  | TTS（音声生成）の詳細          |
| [docs/guide/transcription.md](./docs/guide/transcription.md) | 音声テキスト化、再現度向上  |

---

## 🔍 トラブルシューティング

### 録音できない

1. `voice-clone devices --audio` でデバイス確認
2. `pactl info` で PulseAudio 状態確認
3. Windows のマイク設定を確認

### 生成エラー

- **メモリ不足**: 他のアプリケーションを終了
- **モデルダウンロード失敗**: インターネット接続を確認して再実行

### 音質が悪い

- 参照音声の品質を確認（ノイズが少ないか）
- 録音時間を5〜10秒程度に
- 明瞭に発話した参照音声を使用
