# Morinohito-Editor
<!-- Python (3.10.4) -->
![Python](https://img.shields.io/badge/language-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![version](https://img.shields.io/badge/version-3.10.4-3776AB?style=flat-square&logo=python&logoColor=white)

<img width="769" height="284" alt="image" src="https://github.com/user-attachments/assets/f61d97ca-c1ec-46b7-9b48-9814bbd76018" />

## Download
<a href="https://github.com/Sadc2h4/Morinohito-Editor/releases/tag/v1.4a">
  <img
    src="https://raw.githubusercontent.com/Sadc2h4/brand-assets/main/button/Download_Button_1.png"
    alt="Download .zip"
    height="48"
  />
</a>
<br>
<a href="https://www.dropbox.com/scl/fi/r2ihup8jilpcoobrzqw1o/Morinohito_Editor.zip?rlkey=zwq1qp6sx0bbxc1xuf2ma385g&st=afci7qlc&dl=1">
  <img
    src="https://raw.githubusercontent.com/Sadc2h4/brand-assets/main/button/Download_Button_4.png"
    alt="Download .zip"
    height="48"
  />
</a>
<br>

## 概要
本ツールは『動画画面内の特定のエリアだけを切り取って別の動画として保存』の機能を持つツールが何処にも見つからなかったため，  
手元のPCとこのツールのみで動画の特定座標エリアを切り取って素材化する動作を簡潔できるようにする目的で作成された簡易動画編集ツールです．  
一応，通常の『動画の特定時間部分を切り出すツール』として使用することも可能となっています．  
『動画内で特定の場所の数秒間だけが素材として欲しい』のような場面で役に立つかもしれません．  

## 対応拡張子
・.mp4ファイル  
・.gifファイル  
・.mkvファイル  

## 使い方  


https://github.com/user-attachments/assets/61d0c0df-6f52-41f2-88c3-6fc130b5940b


1. 参照動画ファイルを[選択]ボタンを押して選んでください．形式は.mp4，gif，mkvの3種類から選択可能です．  

2. 動画を参照するとフレーム選択が可能になります．キーボードの左右やマウスで選択フレームを選ぶことが可能です．  
　 フレームを選択時に現在のフレームがプレビューに表示されるので任意のフレームを探します  

3. [選択フレームを参照]ボタンを押すと切り出し座標をクリックで選択できます．
　 フレーム画面が大きすぎる場合は1/2サイズで表示チェック，グリッドが欲しい場合はグリッド有表示チェックを付けてください
   > [!TIP]
　 > 切り出し範囲を指定しない（動画の時間範囲指定抜き出しのみしたい）場合はこの工程は飛ばしてください．  

5. トリミング開始・終了時間を反映ボタンで指定します．[反映]ボタンを押すと現在選択しているフレーム時間が記載されます．  
　 > [!TIP]
   > 開始時間が終了時間よりも後にすることや，0を指定することは出来ないためご注意ください．  
　
5：トリミング開始ボタンを押すと結果が出力されます．  

> [!CAUTION]
> 10分を超えるような長い動画のトリミング時は必ず出力後の動画を再生して内容確認をお願いします．
> PILの仕様によりコンマ秒のフレームがズレるため発生する仕様のためご注意ください.
> また，動画の画質が高画質な場合でも指定秒数が数秒ズレる場合があります．

---
## 動作環境
・Windows 10 および 11にて動作を確認
・Macでの動作は未検証なので注意

## 作成言語
・Python 3.10.4 on win32

## 削除方法
そのままファイルを消去すれば削除可能です
