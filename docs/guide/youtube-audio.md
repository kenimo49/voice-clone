# YouTube からの音声抽出ガイド

YouTube などの動画から音声を抽出し、Voice Clone の参照音声として使用する方法を説明します。

## 注意事項

### 著作権・プライバシーについて

- 他人の声や音声コンテンツには **著作権・肖像権** があります
- **個人的な実験・学習目的** に留めてください
- 商用利用や公開は法的問題が発生する可能性があります
- 本人の許可なく第三者の声をクローンして公開することは避けてください

## 前提条件

yt-dlp がインストールされていること：

```bash
source venv/bin/activate
pip install yt-dlp
```

## 基本的な使い方

### 音声のダウンロード

```bash
# WAV形式でダウンロード
yt-dlp -x --audio-format wav -o "samples/%(title)s.%(ext)s" "YouTubeのURL"

# ファイル名を指定
yt-dlp -x --audio-format wav -o "samples/sample.wav" "YouTubeのURL"
```

### 実行例

```bash
yt-dlp -x --audio-format wav -o "samples/youtube_sample.wav" "https://www.youtube.com/watch?v=XXXXX"
```

出力：

```
[youtube] Extracting URL: https://www.youtube.com/watch?v=XXXXX
[youtube] XXXXX: Downloading webpage
[download] Destination: samples/youtube_sample.webm
[download] 100% of 1.33MiB in 00:00:01
[ExtractAudio] Destination: samples/youtube_sample.wav
Deleting original file samples/youtube_sample.webm
```

## 音声の切り出し

Voice Clone には **5〜10秒程度** の音声が最適です。長い動画から一部を切り出しましょう。

### Python で切り出し

```bash
python -c "
import soundfile as sf

# 読み込み
data, sr = sf.read('samples/youtube_sample.wav')
print(f'Total duration: {len(data)/sr:.2f}s')

# 最初の10秒を切り出し
duration = 10  # seconds
samples = int(sr * duration)
clip = data[:samples]

# 保存
sf.write('samples/youtube_clip.wav', clip, sr)
print(f'Saved: samples/youtube_clip.wav ({duration}s)')
"
```

### 特定の区間を切り出し

```bash
python -c "
import soundfile as sf

data, sr = sf.read('samples/youtube_sample.wav')

# 30秒〜40秒の区間を切り出し
start_sec = 30
end_sec = 40

start_sample = int(sr * start_sec)
end_sample = int(sr * end_sec)
clip = data[start_sample:end_sample]

sf.write('samples/youtube_clip.wav', clip, sr)
print(f'Saved: {start_sec}s - {end_sec}s ({end_sec - start_sec}s)')
"
```

## 音声品質の確認

### 情報を確認

```bash
python -c "
import soundfile as sf
import numpy as np

data, sr = sf.read('samples/youtube_clip.wav')
print(f'Duration: {len(data)/sr:.2f}s')
print(f'Sample rate: {sr}Hz')
print(f'Max amplitude: {np.abs(data).max():.4f}')
"
```

### 再生して確認

```bash
paplay samples/youtube_clip.wav
```

## 良い参照音声の選び方

### 推奨

| 条件 | 説明 |
|------|------|
| **クリアな音声** | BGM やノイズが少ない |
| **単一話者** | 1人だけが話している部分 |
| **自然な発話** | 叫び声や特殊な発声でない |
| **適切な長さ** | 5〜10秒程度 |

### 適した動画の例

- インタビュー動画
- トーク動画
- 解説動画
- ポッドキャスト

### 避けるべき動画

- BGM が大きい
- 複数人が同時に話す
- エフェクトがかかっている
- 音質が悪い

## 対応サイト

yt-dlp は YouTube 以外にも対応しています：

- YouTube / YouTube Shorts
- Twitter (X)
- TikTok
- ニコニコ動画
- その他多数

```bash
# YouTube Shorts
yt-dlp -x --audio-format wav -o "samples/shorts.wav" "https://www.youtube.com/shorts/XXXXX"

# Twitter
yt-dlp -x --audio-format wav -o "samples/twitter.wav" "https://twitter.com/user/status/XXXXX"
```

## トラブルシューティング

### ダウンロードできない

```bash
# yt-dlp を最新版に更新
pip install -U yt-dlp
```

### 「JavaScript runtime」の警告

警告は出ますが、通常は動作します。気になる場合は：

```bash
# deno をインストール（オプション）
curl -fsSL https://deno.land/install.sh | sh
```

### 音声が抽出されない

```bash
# 利用可能なフォーマットを確認
yt-dlp -F "YouTubeのURL"

# 特定のフォーマットを指定
yt-dlp -f 140 -o "samples/audio.m4a" "YouTubeのURL"
```

## 次のステップ

音声を準備できたら、[TTS ガイド](./tts.md)で音声生成を試しましょう。
