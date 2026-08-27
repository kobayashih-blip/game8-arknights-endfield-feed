# Game8 アークナイツ：エンドフィールド RSS

Game8の検索ページから記事名、概要、最終更新日時を取得し、更新日時順のRSS 2.0を生成します。GitHub Actionsが約30分ごとに更新します。

## 公開手順

1. GitHubで `game8-arknights-endfield-feed` という公開リポジトリを作成します。
2. このフォルダの中身をリポジトリへpushします。
3. GitHubの `Settings → Pages` を開きます。
4. `Deploy from a branch`、ブランチ `main`、フォルダ `/docs` を選択します。
5. `Actions` から `Update RSS feed` を一度手動実行します。

Slackへ登録するFeed URL：

```text
https://<GitHubユーザー名>.github.io/game8-arknights-endfield-feed/feed.xml
```

Slackでは対象チャンネルで次を実行できます。

```text
/feed subscribe https://<GitHubユーザー名>.github.io/game8-arknights-endfield-feed/feed.xml
```

GitHub Actionsの定期実行時刻は多少遅れることがあります。Game8側のHTML構造が変わると抽出条件の修正が必要です。
