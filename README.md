# p-intro_app

注意：このリポジトリでは学生の個人情報に関するファイルを削除しているため，そのままでは実行できない．そのため，使用する際は開発者から設定用のファイルを受け取るように．

プログラミング入門のTAの採点業務を効率化するアプリケーションを開発した．これの使い方を説明する．

## 初期画面
最初のページで採点する回の番号を選択する．（要改良）
今回は第6回目の採点をもとに説明する．
![image](https://github.com/itsutose/flask_tutrial/assets/94808308/67ac207d-736c-46e0-a6ea-8dd5fceb017f)

↓

第6回目用のページ：成績一覧ページ
最初の段階では何も表示されない．
![image](https://github.com/itsutose/flask_tutrial/assets/94808308/ac5e1768-4f5c-456f-bff8-2d7669c17f44)

## ファイルのアップロード
採点する学生のipynbのファイルをアップロードする．
成績一覧ページのファイルのアップロードの部分から飛ぶ．

ファイルのアップロードは"Drag and drop files here"の領域にファイルをドラッグ&ドロップすることでできる．
以下はファイルのアップロードページでファイルのアップロード後の様子．

![file_uploaded](https://github.com/itsutose/p-intro_app/assets/94808308/2e68594c-bbe5-416b-a699-fa76c615c5aa)

ファイルをアップロードすると成績一覧ページは以下のようになる．
![seiseki_ichiran](https://github.com/itsutose/p-intro_app/assets/94808308/239b3bb0-d625-42d2-994f-60299b68d79b)


## 採点
成績一覧ページのメニューバーにある「設問」からドロップメニューリストで採点する設問を選択する．
![questions](https://github.com/itsutose/p-intro_app/assets/94808308/a75a4d1e-2690-48c7-8cd7-e7f9f35fd7c4)

### 採点画面
表示される内容
- 設問に対する回答．（プログラムなら実行結果も）
- 採点用の点数，減点箇所，その他コメントの入力欄
  
回答の内容を分類した中で最も多いものをピンク，2番目をを青，3番目を緑のセルになるようにしている．
![saiten](https://github.com/itsutose/p-intro_app/assets/94808308/12b1b015-459c-4b99-a2d4-0777a84b953d)

また，確認用に学生の氏名をクリックするとソースのipynbファイルを参照することができる．
![image](https://github.com/itsutose/flask_tutrial/assets/94808308/38bba8b5-867b-4ead-9ab9-634d8805600b)


採点ページにて点数，減点箇所，その他コメントを記入すると成績一覧ページに反映される．
![seiseki_ichiran_saiten](https://github.com/itsutose/p-intro_app/assets/94808308/2ffd912e-049f-42c6-9230-371ea1288aec)


## Excelへのコピペ
成績一覧ページの表はマウスのドラッグ操作によってセルを選択することができる．
下の図の青い部分が選択されている．この状態でCtrl+Cを押すことで，これらのセルの情報をコピーできる．
![seiseki_copy](https://github.com/itsutose/p-intro_app/assets/94808308/c768c7ac-e1a0-4969-97cb-511436cc2482)

ここでコピーしたものをExcelファイルにペーストする．先ほどコピーした内容をセルの形状を保ったままそのままペーストできる．
![image](https://github.com/itsutose/flask_tutrial/assets/94808308/1c55b32b-4002-4ff7-a9cb-d4c76be8d101)
