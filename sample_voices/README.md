# Sample Voices

Voice Clone のテスト用サンプル音声です。

## 音声ファイル

| ファイル | 説明 | 長さ |
|----------|------|------|
| `mens_voice.wav` | 日本語音声サンプル（男性） | 5秒 |

## 使用例

```bash
voice-clone generate \
  -r sample_voices/mens_voice.wav \
  -t "こんにちは、今日もいい天気ですね" \
  -o outputs/test.wav
```

## 注意事項

- これらの音声は学習・テスト目的でのみ使用してください
- 商用利用や再配布は避けてください
