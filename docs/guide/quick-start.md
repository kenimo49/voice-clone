# クイックスタートガイド

Voice Clone ツールの基本的な使い方を説明します。

## 前提条件

[環境構築ガイド](./environment-setup.md) が完了していること。

## 基本的な流れ

1. **録音**: 自分の声（または参照したい声）を録音
2. **生成**: 録音した声で任意のテキストを読み上げ

## Step 1: 仮想環境の有効化

```bash
cd voice-clone
source venv/bin/activate
```

## Step 2: オーディオデバイスの確認

```bash
voice-clone devices --audio
```

出力例：

```
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Index ┃ Name                       ┃ Type      ┃ Sample Rate ┃ Default ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━┩
│     0 │ RDPSource                  │ Input     │    44100 Hz │ Input   │
│     1 │ RDPSink                    │ Output    │    44100 Hz │ Output  │
└───────┴────────────────────────────┴───────────┴─────────────┴─────────┘
```

`Input` タイプのデバイスがあれば録音可能です。

## Step 3: 音声サンプルの録音

### 固定時間録音（推奨）

5秒間の録音：

```bash
voice-clone record -o samples/my_voice.wav -d 5
```

実行すると：

```
Recording for 5.0 seconds...
Speak now!
Recording finished.
Saved: samples/my_voice.wav
```

**Tips**: 録音中は明瞭に、一定の音量で話してください。3〜10秒程度が最適です。

### インタラクティブ録音

Enter キーで開始/停止する録音：

```bash
voice-clone record -o samples/my_voice.wav --interactive
```

```
Press Enter to start recording...
[Enter]
Recording... Press Enter to stop.
[数秒話す]
[Enter]
Recording stopped.
Saved 4.52 seconds of audio to samples/my_voice.wav
```

## Step 4: 録音の確認

録音したファイルを再生して確認：

```bash
aplay samples/my_voice.wav
```

または、ファイル情報を確認：

```bash
file samples/my_voice.wav
```

## Step 5: 音声生成

録音した声で新しいテキストを読み上げ：

```bash
voice-clone generate \
  -r samples/my_voice.wav \
  -t "こんにちは、今日もいい天気ですね" \
  -o outputs/hello.wav
```

**注意**: 初回実行時はモデルのダウンロードに時間がかかります（約1〜2GB）。

出力例：

```
Reference: samples/my_voice.wav
Text: こんにちは、今日もいい天気ですね
Device: auto
Loading model on cpu...
Model loaded: Qwen/Qwen3-TTS-12Hz-0.6B
Generating speech for: 'こんにちは、今日もいい天気ですね'
Using reference: samples/my_voice.wav
Generated 3.45 seconds of audio to outputs/hello.wav
Generated: outputs/hello.wav
```

## Step 6: 生成した音声の確認

```bash
aplay outputs/hello.wav
```

## コマンドリファレンス

### record コマンド

```bash
# 基本形
voice-clone record -o <出力ファイル> -d <秒数>

# オプション
-o, --output     出力ファイルパス（必須）
-d, --duration   録音時間（秒）
--interactive    インタラクティブモード
--device         オーディオデバイスのインデックス
--sample-rate    サンプルレート（デフォルト: 24000）
--list-devices   デバイス一覧を表示
```

### generate コマンド

```bash
# 基本形
voice-clone generate -r <参照音声> -t <テキスト> -o <出力ファイル>

# オプション
-r, --reference   参照音声ファイル（必須）
-t, --text        読み上げテキスト（必須）
-o, --output      出力ファイルパス（必須）
--device          計算デバイス（auto/cpu/cuda）
--model           モデル名
--sample-rate     サンプルレート（デフォルト: 24000）
```

### devices コマンド

```bash
voice-clone devices --audio  # オーディオデバイス
voice-clone devices --gpu    # GPU情報
voice-clone devices          # 両方
```

## 実践例

### 例1: 複数のテキストを生成

```bash
# 同じ声で複数のファイルを生成
voice-clone generate -r samples/my_voice.wav -t "おはようございます" -o outputs/morning.wav
voice-clone generate -r samples/my_voice.wav -t "お疲れ様でした" -o outputs/goodbye.wav
voice-clone generate -r samples/my_voice.wav -t "ありがとうございます" -o outputs/thanks.wav
```

### 例2: 異なる話者

```bash
# 話者Aの録音
voice-clone record -o samples/speaker_a.wav -d 5

# 話者Bの録音
voice-clone record -o samples/speaker_b.wav -d 5

# それぞれの声で生成
voice-clone generate -r samples/speaker_a.wav -t "私はAです" -o outputs/a_intro.wav
voice-clone generate -r samples/speaker_b.wav -t "私はBです" -o outputs/b_intro.wav
```

### 例3: デバイス指定

特定のマイクを使用する場合：

```bash
# デバイス一覧を確認
voice-clone devices --audio

# デバイス番号を指定して録音
voice-clone record -o samples/test.wav -d 5 --device 2
```

## パフォーマンスについて

| 環境 | 10秒の音声生成 |
|------|---------------|
| CPU（i7-10610U） | 30秒〜1分 |
| GPU（CUDA） | 数秒 |

CPU モードでは生成に時間がかかりますが、品質は同等です。

## 次のステップ

- より長い参照音声を試す（10秒程度）
- 異なるテキストで音声品質を比較
- バッチ処理スクリプトの作成

## トラブルシューティング

### 録音できない

```bash
# デバイスを確認
voice-clone devices --audio

# PulseAudio の状態を確認
pactl info
```

### 生成エラー

- メモリ不足: 他のアプリケーションを終了
- モデルダウンロード失敗: インターネット接続を確認して再実行

### 音質が悪い

- 参照音声の品質を確認（ノイズが少ないか）
- 録音時間を長くする（5〜10秒推奨）
- 明瞭に発話した参照音声を使用
