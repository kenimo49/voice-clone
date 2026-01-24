# Sample Voices

Voice Clone のテスト用サンプル音声です。

## 音声ファイル

| ファイル | 説明 | 長さ |
|----------|------|------|
| `kenimo49_voice.wav` | 録音した日本語音声サンプル | 5秒 |
| `dozuru_voice.wav` | YouTube から抽出した音声サンプル | 10秒 |

## 使用例

```bash
# kenimo49_voice を使用
voice-clone generate \
  -r sample_voices/kenimo49_voice.wav \
  -t "こんにちは、今日もいい天気ですね" \
  -o outputs/test.wav

# dozuru_voice を使用
voice-clone generate \
  -r sample_voices/dozuru_voice.wav \
  -t "こんにちはドズルです！" \
  -o outputs/dozle.wav
```

## 注意事項

- これらの音声は学習・テスト目的でのみ使用してください
- 商用利用や再配布は避けてください
