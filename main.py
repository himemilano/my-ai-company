import os
from crewai import Agent, Crew, Process, Task

# 1. エージェント（AI社員）の設定
pm = Agent(
    role="敏腕プロダクトマネージャー",
    goal="日常のちょっとした悩みを解決する、面白いWebアプリのアイデアを1つ考案する",
    backstory="あなたは数々のヒットアプリを生み出してきた天才PMです。斬新かつ、ブラウザだけで動くシンプルなアプリを考えるのが得意です。",
    verbose=True,
    llm="gemini/gemini-2.5-flash",
)

writer = Agent(
    role="テクニカルライター",
    goal="PMが出したアイデアを整理し、エンジニアがすぐ開発できるMarkdown仕様書を作成する",
    backstory="あなたは分かりやすく美しい構成で技術ドキュメントを書くプロフェッショナルです。",
    verbose=True,
    llm="gemini/gemini-2.5-flash",
)

# ★新入社員：プログラマーを雇用
coder = Agent(
    role="天才フロントエンドエンジニア",
    goal="仕様書を元に、ブラウザで実際に動くHTML/CSS/JavaScriptのコードを作成する",
    backstory="あなたは見た目が美しく、1ファイル（HTMLファイル1枚）で完結するインタラクティブなWebアプリを組み上げる天才プログラマーです。デザインセンスも抜群です。",
    verbose=True,
    llm="gemini/gemini-2.5-flash",
)

# 2. タスク（業務命令）の定義
task1 = Task(
    description="現代人が日常で抱える小さなストレスを解消する、ブラウザで動くミニマルなWebアプリのアイデアを1つ考えてください。",
    expected_output="アプリ名、ターゲット層、解決する悩み、主な機能3つ",
    agent=pm,
)

task2 = Task(
    description="PMのアイデアを元に、実装計画書（仕様書）をMarkdown形式で記述してください。ファイルに保存できるよう美しく整形してください。",
    expected_output="Markdown形式のアプリ仕様書テキスト",
    agent=writer,
    output_file="idea_of_the_day.md",
)

# ★新しいタスク：アプリを実際に作らせる命令
task3 = Task(
    description="ライターが作成した仕様書とPMのアイデアを元に、ブラウザで開くだけで実際に動作するHTML/CSS/JSが1枚にまとまったWebアプリのコードを実装してください。CSSでモダンかつ美しい見た目に装飾し、JSで機能が実際に動くようにしてください。解説などの余計なテキストは一切含めず、純粋なHTMLコードのみを出力ファイルに保存してください。",
    expected_output="実際に動作する完成されたHTML/CSS/JSのコード（純粋なHTMLファイルの内容のみ、```html などのマークダウン枠は不要）",
    agent=coder,
    output_file="index.html", # ★ここに完成品アプリが自動納品されます！
)

# 3. チーム結成と実行（3人体制にアップデート）
my_ai_company = Crew(
    agents=[pm, writer, coder], # プログラマーを追加
    tasks=[task1, task2, task3], # コーディング業務を追加
    process=Process.sequential, # PM → ライター → プログラマーの順に連携
    verbose=True,
)

print("🤖 [社長AI] 本日の業務を開始します（3人体制）...")
result = my_ai_company.kickoff()
print("🤖 [社長AI] 本日の業務が完了しました！仕様書とアプリ本体を納品します。")
