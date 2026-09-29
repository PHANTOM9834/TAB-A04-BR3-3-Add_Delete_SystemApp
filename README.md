# TAB-A04-BR3-3-Add_Delete_App チャレンジタッチ3のシステムアプリの追加、削除自動化ツール for Linux
本ツールを使用した場合、以下の条件にすべて同意したものとみなされます。
本ツールはAndroidシステムのパーティション書き換えを行う高度なツールです。
誤った操作や不具合により、デバイスが起動しなくなる（文鎮化する）等の重大なリスクがあります。
本ツールの使用によるいかなるデータの損失、機器の破損・損害についても、作者は一切の責任を負いません。すべて自己責任でご利用ください。
本ツールを使用するにあたっては、以下の条件を必ず満たしていることをご確認ください：
adb、fastboot、MTKClient のすべてのツールが正常に使用できること。
特に MTKClient は依存関係が複雑かつAndroidの深いシステム階層を扱うため、万が一 fastboot が失敗した際に復旧手段がないと文鎮化します。
重要なパーティション（できればすべてのパーティション）のバックアップを事前に取得しておくこと。
パソコンおよびAndroidのシステム構造に関する十分な知識があること。
作者の検証環境は Python 3.12 / Zorin OS 18.1 です。

Ubuntuベース向けに構築されているため、他のLinuxディストリビューションでは正常に動作しない場合があります。

- **boot.img の準備について:**
  - カスタムした `system.img` を正常に起動させるため、デバイスのビルド番号に一致する公式の `boot.img` を用意し、Magisk 等を用いて `dm-verity`（no-verity）を無効化した状態のものを事前に導入しておいてください。
  - Magiskをboot.imgにご自身でパッチするもしくは安全性、著作権のためここにはリンクを書けませんが、ネット上に公開されているMagiskがパッチされているboot.imgをダウンロードしてください。
  - Magiskをパッチしたboot.imgを入れたらMagiskのAPKをパソコンにダウンロードしてADBでインストールできます。それを開いて追加のファイルをダウンロードするか聞かれたらダウンロードして、再起動されたらもう一度開きインストールを押してdm-verityを維持するにチェックを入れないで直接インストールするを選択したらできます。

チャレンジタッチの `system.img` (`priv-app` / `app`) に対して、アプリフォルダの追加および削除を行えるクロス環境対応のPython GUIツールです。（Linux / Ubuntu系対応 作者は謎にLinuxMintでマウントが読み込み専用だったことがあるためZorinOSを強く推奨します。）

## 主な機能
- `system.img` の安全なマウント・アンマウント処理
- アプリフォルダの追加（パーミッションおよびSELinuxコンテキストの自動設定）
- ターゲットディレクトリ（`priv-app` / `app`）からのアプリ一覧自動取得と削除機能
- 変更内容のディスク同期 (`sync`)

## 動作環境・必要要件
- **OS:** Zorin OS 18.1 推奨（Ubuntuベース。※Linux Mint等ではマウントが読み込み専用になる挙動が確認されているため、Zorin OSの利用を強く推奨します）
- **Python:** Python 3.12 推奨
- **Python ライブラリ:** `customtkinter` `tkinter`

### インストール手順
端末（ターミナル）を開き、必要なパッケージをインストールしてください：
```bash
pip install customtkinter
sudo apt install python3-tk
```

### 仮想環境について
- LinuxではWindowsのようにPythonライブラリをpipで追加しようとすると以下のようにエラーになります。
- そのためvenvを使用して仮想環境を構築してその中でライブラリの追加、Pythonスクリプトの実行をすることを推奨します。
- どうしても仮想環境を使用したくないのであれば `--break-system-packages` を使用する方法もありますがあまりおすすめはできません。
```markdown
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.  
```
