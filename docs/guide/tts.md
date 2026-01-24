# TTS（音声生成）ガイド

Qwen3-TTS を使用して、参照音声の声で任意のテキストを読み上げる方法を説明します。

## 概要

Voice Clone の TTS 機能は、参照音声から話者の特徴を抽出し、指定したテキストをその声で読み上げた音声を生成します。

## 前提条件

- 参照音声が準備されていること
  - [録音ガイド](./recording.md)
  - [YouTube からの音声抽出ガイド](./youtube-audio.md)
- モデルのダウンロード用にインターネット接続があること

## 基本的な使い方

### 音声生成コマンド

```bash
voice-clone generate \
  -r samples/reference.wav \
  -t "読み上げたいテキスト" \
  -o outputs/output.wav
```

### オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-r, --reference` | 参照音声ファイル（必須） | - |
| `-t, --text` | 読み上げテキスト（必須） | - |
| `-o, --output` | 出力ファイルパス（必須） | - |
| `--device` | 計算デバイス | auto |
| `--model` | モデル名 | Qwen/Qwen3-TTS-12Hz-0.6B-Base |
| `--sample-rate` | サンプルレート | 24000 |
| `--temperature` | 音声のテンション調整 | 1.0 |

## 実行例

### 基本的な生成

```bash
voice-clone generate \
  -r samples/my_voice.wav \
  -t "こんにちは、今日もいい天気ですね" \
  -o outputs/hello.wav
```

出力：

```
Reference: samples/my_voice.wav
Text: こんにちは、今日もいい天気ですね
Device: auto
Loading model on cpu...
Model loaded: Qwen/Qwen3-TTS-12Hz-0.6B-Base
Generating speech for: 'こんにちは、今日もいい天気ですね'
Using reference: samples/my_voice.wav
Generated 2.38 seconds of audio to outputs/hello.wav
Generated: outputs/hello.wav
```

### 複数のテキストを生成

```bash
# 同じ声で複数のファイルを生成
voice-clone generate -r samples/speaker.wav -t "おはようございます" -o outputs/morning.wav
voice-clone generate -r samples/speaker.wav -t "お疲れ様でした" -o outputs/evening.wav
voice-clone generate -r samples/speaker.wav -t "ありがとうございます" -o outputs/thanks.wav
```

### デバイス指定

```bash
# CPU を明示的に指定
voice-clone generate -r samples/speaker.wav -t "テスト" -o outputs/test.wav --device cpu

# GPU を使用（CUDA環境）
voice-clone generate -r samples/speaker.wav -t "テスト" -o outputs/test.wav --device cuda
```

## 生成した音声の確認

### 再生

```bash
paplay outputs/hello.wav
```

### 情報確認

```bash
python -c "
import soundfile as sf
data, sr = sf.read('outputs/hello.wav')
print(f'Duration: {len(data)/sr:.2f}s')
print(f'Sample rate: {sr}Hz')
"
```

## モデルについて

### 利用可能なモデル

| モデル名 | パラメータ | サイズ | 推奨環境 | 品質 |
|----------|-----------|--------|----------|------|
| `Qwen/Qwen3-TTS-12Hz-0.6B-Base` | 0.6B | 約 1-2GB | CPU / GPU | 良好 |
| `Qwen/Qwen3-TTS-12Hz-1.7B-Base` | 1.7B | 約 3-4GB | GPU（VRAM 8GB+） | より高品質 |

**デフォルト**: `Qwen/Qwen3-TTS-12Hz-0.6B-Base`（軽量版）

### モデルの選択

#### GPU 環境で高品質モデルを使用

```bash
# 1.7B モデルを指定（GPU推奨）
voice-clone generate \
  -r samples/speaker.wav \
  -t "こんにちは" \
  -o outputs/hello.wav \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-Base \
  --device cuda
```

#### 環境別の推奨設定

| 環境 | モデル | デバイス |
|------|--------|----------|
| CPU のみ | `Qwen/Qwen3-TTS-12Hz-0.6B-Base` | `--device cpu` |
| GPU（VRAM 4GB） | `Qwen/Qwen3-TTS-12Hz-0.6B-Base` | `--device cuda` |
| GPU（VRAM 8GB+） | `Qwen/Qwen3-TTS-12Hz-1.7B-Base` | `--device cuda` |

#### エイリアスの設定（オプション）

頻繁に使う場合は、シェルにエイリアスを設定すると便利です：

```bash
# ~/.bashrc に追加
alias vc-cpu='voice-clone generate --model Qwen/Qwen3-TTS-12Hz-0.6B-Base --device cpu'
alias vc-gpu='voice-clone generate --model Qwen/Qwen3-TTS-12Hz-1.7B-Base --device cuda'
```

使用例：

```bash
vc-gpu -r samples/speaker.wav -t "こんにちは" -o outputs/hello.wav
```

### 対応言語

Qwen3-TTS は以下の10言語に対応しています：

- 日本語、中国語、英語、韓国語、ドイツ語
- フランス語、ロシア語、ポルトガル語、スペイン語、イタリア語

### 初回実行

初回実行時にモデルが自動ダウンロードされます。

| モデル | ダウンロードサイズ |
|--------|-------------------|
| 0.6B | 約 1-2GB |
| 1.7B | 約 3-4GB |

```
Fetching 4 files: 100%|██████████| 4/4 [00:26<00:00, 6.65s/it]
```

### モデルのキャッシュ

ダウンロードされたモデルは `~/.cache/huggingface/` に保存され、次回以降は再利用されます。

## パフォーマンス

### 処理時間の目安

| 環境 | モデル | 10秒の音声生成 |
|------|--------|---------------|
| CPU（i7-10610U） | 0.6B | 30秒〜1分 |
| GPU（RTX 3060） | 0.6B | 2〜3秒 |
| GPU（RTX 3060） | 1.7B | 5〜10秒 |

### GPU の確認

```bash
voice-clone devices --gpu
```

```
                GPU Information
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property       ┃ Value                  ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ CUDA Available │ No                     │
│ Device Count   │ 0                      │
│ Note           │ CPU mode will be used  │
└────────────────┴────────────────────────┘
```

## 音声のテンション調整

`--temperature` オプションで音声のテンション（抑揚・エネルギー）を調整できます。

### temperature の効果

| 値 | 効果 | 用途 |
|----|------|------|
| 0.7〜0.9 | 落ち着いた・安定した音声 | ナレーション、解説 |
| 1.0（デフォルト） | 標準的な音声 | 一般的な用途 |
| 1.2〜1.5 | 元気・ハイテンションな音声 | キャラクターボイス、挨拶 |

### 使用例

```bash
# 落ち着いたナレーション
voice-clone generate \
  -r samples/speaker.wav \
  -t "本日のニュースをお伝えします" \
  -o outputs/news.wav \
  --temperature 0.8

# 元気な挨拶
voice-clone generate \
  -r samples/speaker.wav \
  -t "こんにちは！今日も元気にいきましょう！" \
  -o outputs/greeting.wav \
  --temperature 1.3
```

### テキストとの組み合わせ

テンション調整は **テキストの書き方** と組み合わせると効果的です：

| テクニック | 効果 |
|-----------|------|
| 「！」を使う | より強調された発話 |
| 「〜」を使う | 柔らかい印象 |
| 句読点を増やす | ゆっくりした発話 |

```bash
# 高テンション：temperatureとテキストの組み合わせ
voice-clone generate \
  -r samples/speaker.wav \
  -t "やったー！最高です！ありがとうございます！" \
  -o outputs/excited.wav \
  --temperature 1.3
```

## 音声品質を上げるコツ

### 参照音声

- **クリアな音声**: ノイズが少ないほど良い
- **適切な長さ**: 5〜10秒が最適
- **自然な発話**: 明瞭でテンポが安定している

### テキスト

- **自然な文**: 句読点を適切に使う
- **適切な長さ**: 長すぎると品質が低下することがある
- **言語一致**: 参照音声と同じ言語が望ましい

## 対応言語

Qwen3-TTS は以下の言語に対応しています：

- 日本語
- 中国語
- 英語
- 韓国語
- ドイツ語
- フランス語
- ロシア語
- ポルトガル語
- スペイン語
- イタリア語

## トラブルシューティング

### メモリ不足

```
RuntimeError: CUDA out of memory
```

- `--device cpu` を使用
- 他のアプリケーションを終了

### モデルダウンロード失敗

```
HTTPError: 403 Forbidden
```

- インターネット接続を確認
- 再実行してみる
- プロキシ設定を確認

### 生成が遅い

- CPU モードでは時間がかかるのは正常
- GPU が利用可能なら `--device cuda` を試す

### 音質が悪い

- 参照音声の品質を確認
- 参照音声を長くする（10秒程度）
- ノイズのない参照音声を使用

## 応用例

### バッチ処理スクリプト

```bash
#!/bin/bash
REFERENCE="samples/speaker.wav"

texts=(
    "おはようございます"
    "こんにちは"
    "こんばんは"
    "おやすみなさい"
)

for i in "${!texts[@]}"; do
    voice-clone generate \
        -r "$REFERENCE" \
        -t "${texts[$i]}" \
        -o "outputs/greeting_$i.wav"
done
```

### Python からの利用

```python
from voice_clone.tts.qwen_tts import QwenTTS
from voice_clone.config import TTSConfig
from pathlib import Path

config = TTSConfig(device="cuda")
tts = QwenTTS(config=config)

# 通常の生成
tts.generate(
    text="こんにちは",
    reference_audio=Path("samples/speaker.wav"),
    output_path=Path("outputs/hello.wav"),
)

# テンション高めで生成
tts.generate(
    text="やったー！最高です！",
    reference_audio=Path("samples/speaker.wav"),
    output_path=Path("outputs/excited.wav"),
    temperature=1.3,
)
```

## 次のステップ

- 異なる参照音声で結果を比較
- 長いテキストの生成を試す
- バッチ処理で複数ファイルを生成
