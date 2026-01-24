# 音声テキスト化（STT）ガイド

Vosk を使用して音声ファイルをテキストに変換する方法を説明します。

## 概要

Voice Clone の STT（Speech-to-Text）機能は、Vosk エンジンを使用してローカルで音声認識を行います。インターネット接続不要で、無料で利用できます。

## 前提条件

- voice-clone がインストールされていること
- 音声ファイル（WAV 形式推奨）

## 基本的な使い方

### 音声ファイルをテキスト化

```bash
voice-clone transcribe -i <音声ファイル>
```

### 例

```bash
# 日本語音声をテキスト化
voice-clone transcribe -i samples/speaker.wav

# 英語音声をテキスト化
voice-clone transcribe -i samples/english.wav -l en
```

## コマンドオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-i, --input` | 入力音声ファイル（必須） | - |
| `-l, --language` | 言語コード（ja, en, zh） | ja |

## 対応言語

| 言語 | コード | モデル名 | サイズ |
|------|--------|----------|--------|
| 日本語 | `ja` | vosk-model-small-ja-0.22 | 約 48MB |
| 英語 | `en` | vosk-model-small-en-us-0.15 | 約 40MB |
| 中国語 | `zh` | vosk-model-small-cn-0.22 | 約 42MB |

## モデルのダウンロード

### 自動ダウンロード

初回実行時にモデルが自動的にダウンロードされます。

```bash
voice-clone transcribe -i samples/speaker.wav
# → モデルが ~/.voice-clone/models/ にダウンロードされる
```

### 事前ダウンロード

モデルを事前にダウンロードしておくこともできます。

```bash
# 日本語モデル
voice-clone download-model

# 英語モデル
voice-clone download-model -l en

# 中国語モデル
voice-clone download-model -l zh
```

### モデルの保存場所

```
~/.voice-clone/models/
├── vosk-model-small-ja-0.22/
├── vosk-model-small-en-us-0.15/
└── vosk-model-small-cn-0.22/
```

## TTS との連携

### 参照テキスト（ref-text）による再現度向上

音声クローンの再現度を向上させるには、参照音声の内容（何を話しているか）をテキストとして提供することが重要です。

#### なぜ ref-text が効果的か

| モード | 仕組み | 再現度 |
|--------|--------|--------|
| ref-text なし | 音声から話者特徴（x-vector）のみを抽出 | 標準 |
| ref-text あり | 音声とテキストの対応関係を理解して話者特徴を抽出 | **向上** |

モデルに「この音声でこのテキストを話している」という知識（knowledge）を与えることで、より正確に話者の特徴を学習できます。

#### 推奨ワークフロー

```bash
# Step 1: 参照音声をテキスト化
voice-clone transcribe -i samples/speaker.wav
# → Result: こんにちは今日はいい天気ですね

# Step 2: 認識結果を確認・修正（句読点追加など）
# 「こんにちは今日はいい天気ですね」→「こんにちは、今日はいい天気ですね」

# Step 3: 修正したテキストを ref-text として使用
voice-clone generate \
  -r samples/speaker.wav \
  --ref-text "こんにちは、今日はいい天気ですね" \
  -t "明日も晴れるといいですね" \
  -o outputs/output.wav
```

#### 効果の比較

| 方法 | 再現度 | 手間 |
|------|--------|------|
| ref-text なし | ★★☆ | なし |
| --auto-transcribe（自動認識） | ★★★ | なし |
| ref-text 手動指定（正確なテキスト） | ★★★★ | 少し |

> **Tips**: 最高の再現度を得るには、参照音声の内容を正確に書き起こして `--ref-text` に指定してください。

### --auto-transcribe オプション

`generate` コマンドで `--auto-transcribe` を使うと、参照音声を自動でテキスト化して `--ref-text` として使用します。

```bash
voice-clone generate \
  -r samples/speaker.wav \
  --auto-transcribe \
  -t "新しいテキスト" \
  -o outputs/output.wav
```

### 手動で ref-text を指定

より正確な結果が必要な場合は、手動でテキストを指定することをおすすめします。

```bash
# 1. まず音声をテキスト化
voice-clone transcribe -i samples/speaker.wav
# → Result: こんにちは今日はいい天気ですね

# 2. 認識結果を確認・修正して ref-text に使用
voice-clone generate \
  -r samples/speaker.wav \
  --ref-text "こんにちは、今日はいい天気ですね" \
  -t "明日も晴れるといいですね" \
  -o outputs/output.wav
```

## Python からの利用

```python
from voice_clone.stt import VoskSTT
from pathlib import Path

# STT エンジンを初期化
stt = VoskSTT(language="ja")

# 音声ファイルをテキスト化
text = stt.transcribe(Path("samples/speaker.wav"))
print(f"認識結果: {text}")
```

### 英語の場合

```python
stt = VoskSTT(language="en")
text = stt.transcribe(Path("samples/english.wav"))
```

### モデルのダウンロード

```python
from voice_clone.stt import download_model

# 日本語モデルをダウンロード
model_path = download_model("ja")
print(f"Model downloaded to: {model_path}")
```

## 対応音声フォーマット

| フォーマット | 対応 | 備考 |
|-------------|------|------|
| WAV | ○ | 推奨 |
| FLAC | ○ | soundfile がサポート |
| OGG | ○ | soundfile がサポート |
| MP3 | △ | 変換が必要な場合あり |

### サンプルレート

- 入力音声は自動的に 16kHz にリサンプリングされます
- 元のサンプルレートに制限はありません

### チャンネル

- ステレオ音声は自動的にモノラルに変換されます

## 認識精度について

### 精度に影響する要素

| 要素 | 影響 | 対策 |
|------|------|------|
| 背景ノイズ | 大 | 静かな環境で録音 |
| 音声の明瞭さ | 大 | はっきりと発話 |
| 音量 | 中 | 適切な入力レベル |
| 話速 | 小 | 普通の速度で |

### 認識精度の目安

| 条件 | 精度 |
|------|------|
| クリアな音声、標準的な発話 | 高い |
| 多少のノイズあり | 中程度 |
| BGM付き、複数人の声 | 低い |

## トラブルシューティング

### モデルのダウンロードが失敗する

```
requests.exceptions.ConnectionError
```

- インターネット接続を確認
- プロキシ設定を確認
- 再試行する

### 認識結果が空になる

```
Result: (empty)
```

- 音声ファイルに発話が含まれているか確認
- 音量が十分か確認
- 言語設定が正しいか確認（`-l` オプション）

### メモリ不足

```
MemoryError
```

- 長い音声ファイルは分割して処理
- 他のアプリケーションを終了

### 認識結果が文字化けする

- 言語設定を確認（日本語なら `-l ja`）
- 別の言語モデルを試す

## 制限事項

- リアルタイム認識には対応していません（ファイルベースのみ）
- 話者識別（誰が話しているか）には対応していません
- 句読点は自動挿入されません
- 方言や強いアクセントは認識精度が低下する場合があります

## 関連ドキュメント

- [TTS（音声生成）ガイド](./tts.md)
- [録音ガイド](./recording.md)
- [クイックスタート](./quick-start.md)
