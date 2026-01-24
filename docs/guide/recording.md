# 録音ガイド

Voice Clone で使用する参照音声の録音方法を説明します。

## 概要

Voice Clone では、参照音声（クローンしたい声のサンプル）を使用して音声を生成します。
高品質な参照音声を用意することで、より良い結果が得られます。

## 録音の前提条件

- WSLg のオーディオ設定が完了していること（[環境構築ガイド](./environment-setup.md)参照）
- マイクが正しく認識されていること

## デバイスの確認

録音前にオーディオデバイスを確認します。

```bash
voice-clone devices --audio
```

出力例：

```
                         Audio Devices
┏━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Index ┃ Name    ┃ Type         ┃ Sample Rate ┃ Default       ┃
┡━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│     0 │ pulse   │ Input/Output │    44100 Hz │               │
│     1 │ default │ Input/Output │    44100 Hz │ Input, Output │
└───────┴─────────┴──────────────┴─────────────┴───────────────┘
```

`Input` タイプのデバイスがあれば録音可能です。

## 録音方法

### 方法1: 固定時間録音（推奨）

指定した秒数だけ録音します。

```bash
# 5秒間録音
voice-clone record -o samples/my_voice.wav -d 5

# 10秒間録音
voice-clone record -o samples/my_voice.wav -d 10
```

実行すると：

```
Recording for 5.0 seconds...
Speak now!
Recording finished.
Saved: samples/my_voice.wav
```

**「Speak now!」が表示されたらすぐに話し始めてください。**

### 方法2: インタラクティブ録音

Enter キーで開始/停止を制御します。

```bash
voice-clone record -o samples/my_voice.wav --interactive
```

```
Press Enter to start recording...
[Enter]
Recording... Press Enter to stop.
[話す]
[Enter]
Recording stopped.
Saved 4.52 seconds of audio to samples/my_voice.wav
```

### 方法3: デバイス指定

特定のマイクを使用する場合：

```bash
# デバイス番号2を使用
voice-clone record -o samples/my_voice.wav -d 5 --device 2
```

## 録音のコツ

### 推奨設定

| 項目 | 推奨値 |
|------|--------|
| 録音時間 | 5〜10秒 |
| 環境 | 静かな場所 |
| 音量 | 一定に保つ |
| 発話 | 明瞭に |

### 良い録音のポイント

1. **静かな環境**: エアコン、換気扇などのノイズを避ける
2. **一定の距離**: マイクから20〜30cm程度
3. **明瞭な発話**: はっきりと、自然なスピードで
4. **適切な音量**: 大きすぎず、小さすぎず

### 避けるべきこと

- BGM や環境音が入る
- マイクに近すぎる（ポップノイズの原因）
- 早口や不明瞭な発話
- 途中で音量が変わる

## 録音の確認

### 音声レベルの確認

```bash
python -c "
import soundfile as sf
import numpy as np
data, sr = sf.read('samples/my_voice.wav')
print(f'Duration: {len(data)/sr:.2f}s')
print(f'Max amplitude: {np.abs(data).max():.4f}')
print(f'Mean amplitude: {np.abs(data).mean():.6f}')
"
```

**目安**:
- Max amplitude: 0.1〜0.9（0.01以下は音量不足）
- Duration: 5〜10秒

### 再生して確認

```bash
paplay samples/my_voice.wav
```

## トラブルシューティング

### 録音できない

```bash
# PulseAudio の状態確認
pactl info

# 環境変数確認
echo $PULSE_SERVER
```

### 音量が小さい

- Windows のマイク設定でレベルを上げる
- マイクに近づく
- 大きめの声で話す

### ノイズが多い

- 静かな環境で録音
- ノイズキャンセリング機能があればオン
- 録音時間を短くして必要な部分だけ録音

## 次のステップ

録音が完了したら、[TTS ガイド](./tts.md)で音声生成を試しましょう。
