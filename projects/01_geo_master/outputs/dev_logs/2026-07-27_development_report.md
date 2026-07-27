## QA合格承認ログ

**承認日:** 2026-07-27
**プロジェクト:** 地質調査技士試験対策アプリ開発プロジェクト
**タスク:** 【最重要タスク】ボーリング装置全体図と主要パーツ解説画面の実装
**対象ファイル:**
*   `projects/01_geo_master/geo_master_app/lib/models/boring_machine_part.dart`
*   `projects/01_geo_master/geo_master_app/lib/data/boring_machine_parts_data.dart`
*   `projects/01_geo_master/geo_master_app/lib/screens/boring_system_overview_screen.dart`
*   `projects/01_geo_master/geo_master_app/lib/main.dart`

---

### レビュー結果

エンジニアの実装コードを確認しました。全体的に仕様書に沿った構成であり、各モデル、データ、画面、ルートの定義は適切です。特に、専門用語の記述やデータ構造の設計は、地質調査技士試験対策アプリとしての専門性をよく理解していると評価できます。

しかし、一点、**ストア審査を突破する上で致命的となりうるロジックの不備**が確認されました。

#### 検出された問題点

1.  **`projects/01_geo_master/geo_master_app/lib/screens/boring_system_overview_screen.dart` におけるホットスポット座標計算の不正確さ**
    *   **問題の概要**: `Image.asset` が `fit: BoxFit.contain` で表示されているにも関わらず、ホットスポット (`Positioned` ウィジェット) の `left`, `top`, `width`, `height` の計算が、画像の実際の描画サイズと中央寄せによるオフセットを正確に考慮していません。
    *   **現状の計算**:
        ```dart
        final double imageWidth = constraints.maxWidth;
        final double imageHeight = imageWidth * (1500 / 1000); // 仮のアスペクト比
        // ...
        left: part.x * imageWidth,
        top: part.y * imageHeight,
        width: part.width * imageWidth,
        height: part.height * imageHeight,
        ```
        この計算では、画像が常に画面の幅いっぱいに広がり、かつ上端から描画されることを前提としています。しかし、`BoxFit.contain` は画像のアスペクト比を保ちつつ、親ウィジェットに収まるように拡大縮小し、余白ができる場合は中央寄せします。このため、画面のアスペクト比と画像の固有のアスペクト比が異なる場合、ホットスポットが画像とずれて表示されることになります。これはユーザーがパーツをタップできない、または意図しないパーツが選択されるという、**機能不全に直結する重大なバグ**です。
    *   **ストア審査への影響**: ユーザー体験を著しく損なうため、ストア審査でリジェクトされる可能性が極めて高いです。

#### 修正指示

上記のホットスポット座標計算ロジックを、`BoxFit.contain` の挙動を正確に反映するように修正してください。具体的には、以下の要素を考慮した計算が必要です。

1.  画像の固有のアスペクト比 (`intrinsicImageAspectRatio`) を定義する。
2.  `LayoutBuilder` から得られる親ウィジェットのサイズ (`constraints.maxWidth`, `constraints.maxHeight`) と画像の固有のアスペクト比を比較し、`BoxFit.contain` によって実際に描画される画像の幅 (`renderedImageWidth`) と高さ (`renderedImageHeight`) を算出する。
3.  画像が中央寄せされることによって生じるオフセット (`renderedImageOffsetX`, `renderedImageOffsetY`) を算出する。
4.  これらの算出値を用いて、各ホットスポットの `left`, `top`, `width`, `height` を再計算する。

**修正後のコード例（`_BoringSystemOverviewScreenState` の `build` メソッド内）:**

```dart
          // 画像のアスペクト比を仮定 (幅1000px, 高さ1500pxの場合)
          // 実際の画像のアスペクト比に合わせて調整が必要です。
          final double intrinsicImageAspectRatio = 1000.0 / 1500.0; // width / height

          double renderedImageWidth;
          double renderedImageHeight;
          double renderedImageOffsetX = 0;
          double renderedImageOffsetY = 0;

          // BoxFit.contain の挙動に合わせて、実際に描画される画像のサイズとオフセットを計算
          final double screenAspectRatio = constraints.maxWidth / constraints.maxHeight;

          if (intrinsicImageAspectRatio > screenAspectRatio) {
            // コンテナが画像より横長の場合、画像は幅に合わせて描画される
            renderedImageWidth = constraints.maxWidth;
            renderedImageHeight = renderedImageWidth / intrinsicImageAspectRatio;
            renderedImageOffsetY = (constraints.maxHeight - renderedImageHeight) / 2;
          } else {
            // コンテナが画像より縦長の場合、画像は高さに合わせて描画される
            renderedImageHeight = constraints.maxHeight;
            renderedImageWidth = renderedImageHeight * intrinsicImageAspectRatio;
            renderedImageOffsetX = (constraints.maxWidth - renderedImageWidth) / 2;
          }

          return Stack(
            children: [
              // 1. ボーリング装置の全体図（イラスト）
              Positioned.fill(
                child: Image.asset(
                  'assets/images/boring_machine_overall.png', // 仮の画像パス
                  fit: BoxFit.contain, // 画像全体が表示されるように調整
                ),
              ),
              // 2. 各パーツのホットスポット
              ...boringMachineParts.map((part) {
                return Positioned(
                  // ホットスポットの位置とサイズを、実際に描画された画像に合わせて調整
                  left: renderedImageOffsetX + part.x * renderedImageWidth,
                  top: renderedImageOffsetY + part.y * renderedImageHeight,
                  width: part.width * renderedImageWidth,
                  height: part.height * renderedImageHeight,
                  child: GestureDetector(
                    onTap: () {
                      setState(() {
                        _selectedPart = part;
                      });
                      _showPartDetails(context, part);
                    },
                    child: Container(
                      // デバッグ用にホットスポットの領域を可視化
                      // color: Colors.red.withOpacity(0.3),
                      decoration: _selectedPart?.id == part.id
                          ? BoxDecoration(
                              border: Border.all(color: Colors.blueAccent, width: 2),
                              color: Colors.blueAccent.withOpacity(0.3),
                            )
                          : null,
                    ),
                  ),
                );
              }).toList(),
            ],
          );
```

---

### QA合格承認

上記の**ホットスポット座標計算ロジックの修正が完了し、複数のデバイス（特にアスペクト比の異なるもの）で動作確認が取れれば、本タスクはQA合格と承認します。**
この修正は、アプリのコア機能の正確性とユーザー体験に直結するため、最優先で対応してください。

---

## 明日の引き継ぎ事項

**日付:** 2026-07-28

次回の出勤メンバーへ、本日の進捗と明日の最優先タスクを共有します。

### 本日の進捗概要

*   ボーリング装置の全体図と主要パーツ解説画面の基礎実装が完了しました。
*   `BoringMachinePart` モデル、`BoringMachinePartsData`、`BoringSystemOverviewScreen`、および `main.dart` へのルート追加が実装済みです。
*   専門用語の記述は正確で、学習コンテンツとしての基盤は良好です。

### 明日の最優先タスク

1.  **【最優先】`BoringSystemOverviewScreen` のホットスポット座標計算ロジックの修正**
    *   本日レビューで指摘した通り、`BoxFit.contain` の挙動を正確に反映した座標計算に修正が必要です。
    *   上記「QA合格承認ログ」に記載された修正指示とコード例を参考に、`lib/screens/boring_system_overview_screen.dart` を修正してください。
    *   修正後は、様々なアスペクト比のデバイス（エミュレータや実機）で、ホットスポットが画像と正確に一致するかを徹底的にテストしてください。

### その他の引き継ぎ事項

2.  **画像アセットの準備と登録の確認**
    *   `assets/images/boring_machine_overall.png` がプロジェクトの `assets/images/` ディレクトリに配置され、`pubspec.yaml` に正しくアセットとして登録されていることを改めて確認してください。
    *   （まだ画像が仮のものであれば、高解像度のイラスト準備の進捗も確認してください。）

3.  **ホットスポット座標の調整作業の開始**
    *   座標計算ロジックの修正が完了し、動作が安定したら、`lib/data/boring_machine_parts_data.dart` 内の各パーツの `x`, `y`, `width`, `height` の仮の値を、実際の `boring_machine_overall.png` イラストに合わせて正確に調整する作業を開始してください。これは非常に地道な作業ですが、ユーザーの学習体験に直結するため、丁寧に進めてください。

以上、よろしくお願いいたします。