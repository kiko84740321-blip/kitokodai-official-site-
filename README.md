# KITOKODAI Official Site — 自動リリース更新版

## この版でできること
- YouTubeチャンネル `@kitokodai` の公開動画を取得
- Apple Music のアーティストページからアルバム／シングル情報を取得
- 曲名が一致するMVと配信作品をできる範囲で重複統合
- 新しい日付順に並べ、サイトには最新3件を表示
- GitHub Actions が6時間ごとに情報を更新
- 「RECOMMEND / PICK UP」は `config.js` で手動編集でき、自動更新に上書きされない

**注意:** Amazon Music Web APIは現時点でクローズドベータで、承認済み開発者以外は使えません。そのため、この版ではYouTube＋Apple Musicを自動取得します。Amazon側はリンク表示・将来のAPI追加に対応できる設計です。

## 1. GitHubにアップロード
1. GitHubで新しいリポジトリを作成（例: `kitokodai-official-site`）。
2. このZIPの中身をすべてリポジトリのルートにアップロードします。`.github/workflows/update-releases.yml` と `scripts/update-releases.mjs` も必要です。
3. `Settings → Pages` で `Deploy from a branch`、Branch=`main`、Folder=`/(root)` を選んで保存します。

## 2. YouTube APIキーを作る
1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成。
2. `YouTube Data API v3` を有効化。
3. `認証情報` からAPIキーを作成。
4. GitHubリポジトリの `Settings → Secrets and variables → Actions → New repository secret` で名前 `YOUTUBE_API_KEY`、値をAPIキーにして保存。

## 3. Apple Music APIトークンを用意
1. [Apple Developer](https://developer.apple.com/) のアカウントで MusicKit / Apple Music API の開発者トークンを生成します。
2. 生成したBearer tokenをGitHub Actions secret `APPLE_MUSIC_TOKEN` に登録します。
3. Apple Music APIの開発者トークンは期限を設定して発行する必要があり、期限切れ時には更新が必要です。APIの利用条件やアカウント要件はAppleの最新ドキュメントを確認してください。

**秘密情報を `config.js` やHTMLに直接書かないでください。** GitHub Secretsに入れることで、ブラウザにAPIキーやトークンが公開されるのを避けます。

## 4. 初回の更新
1. リポジトリの `Actions` タブを開く。
2. `Update latest releases` を選び、`Run workflow` を実行。
3. 実行が成功すると `data/releases.json` が自動コミットされます。
4. GitHub Pagesのサイトを開き、最新3件が表示されることを確認します。
5. 以後は6時間ごとに自動実行されます。

## 5. おすすめ曲を手動で変える
`config.js` の `featured` だけを編集します。

```js
featured: {
  title: "おすすめしたい曲名",
  label: "KITOKODAI / PICK UP",
  description: "この曲の紹介文",
  artText: "おすすめ曲名",
  url: "https://www.youtube.com/watch?v=動画ID"
}
```

おすすめ曲は自動更新対象ではありません。`config.js` を変更してGitHubへ反映すれば、PICK UP枠だけ変わります。

## 6. 自動更新の仕様と注意
- 更新頻度は6時間ごとです。新作公開直後に即時反映されるとは限りません。
- YouTube側はチャンネルのアップロード一覧を見ます。タイトルに `#short` / `#shorts` / `ショート動画` が含まれる動画は除外しますが、通常動画の告知・配信アーカイブなどをMVと誤認する可能性があります。
- Apple Music側はアーティストのアルバム／シングル一覧を見ます。配信開始からAPI掲載までタイムラグが生じる場合があります。
- 同じ曲名の動画と配信作品はタイトルの正規化で統合しますが、表記が大きく違う場合は重複することがあります。
- Apple Music APIトークンが失効したりAPI制限に達したりすると更新が失敗します。GitHub Actionsの実行ログで原因を確認できます。
- Amazon Musicは公式APIの一般公開後、またはアクセス承認後に追加できます。

## ファイル構成
- `index.html`: サイト本体
- `config.js`: 手動で変更するおすすめ曲枠
- `data/releases.json`: 自動取得した最新作品データ
- `scripts/update-releases.mjs`: YouTube／Apple Music取得・重複統合処理
- `.github/workflows/update-releases.yml`: 6時間ごとの自動実行設定
- `assets/kitoko-logo.jpg`: ロゴ
