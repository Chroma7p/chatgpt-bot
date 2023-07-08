# Discord-bot-starter-kit

Discord.py　を使ってDiscordbotを作るための参考になるように、あらゆる機能を詰め込もうと考えているものです。
今のところは最低限のコマンドやコグの使用のみです。

## とりあえず動かす
### トークンの取得とサーバへの加入
[このページ](https://discordpy.readthedocs.io/ja/latest/discord.html)を参考にトークンを取得して、自分で適当なテスト用discordサーバーを作ってそこに入れてください。
具体的には、[discordのapplicationのページ](https://discord.com/developers/applications)に行って、右上の`NewApplication`から、新たなアプリケーションを作成、設定を済ませてから、左のメニューから`Bot`を選び、`Add Bot`でBotを追加(名前が被ってると怒られるので、`Application`から直す)します。
下の`Privileged Gateway Intents`というところに行き、3つともオンにします(受け取れる情報の範囲の設定です、この記事の内容および個人利用であれば全てオンで大丈夫です。)
それができたらBotとして設定とトークンの取得を行い、左のメニューから`OAuth2`→`URL Generator`のページに行き、付与する権限を決めてURLを生成すると、サーバー加入のためのURLを生成できます。
先ほど取得したトークンを`.env.sample`を参考に、`.env`ファイルを作成して入れてください。
(もしくは環境変数にDISCORD_BOT_TOKENとして置いてください)

### 環境構築
流石に最低限Python3.10くらいの環境が出来ているとします。
このプロジェクトのルートディレクトリ(多分discor-bot-starter-kit)で

```
pip install -r requirements.txt
```
で必要なものがインストールされます。






