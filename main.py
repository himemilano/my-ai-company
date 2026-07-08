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

task3 = Task(
    description="ライターが作成した仕様書とPMのアイデアを元に、ブラウザで開くだけで実際に動作するHTML/CSS/JSが1枚にまとまったWebアプリのコードを実装してください。CSSでモダンかつ美しい見た目に装飾し、JSで機能が実際に動くようにしてください。余計な解説テキストは一切含めず、純粋なHTMLコードのみを出力してください。",
    expected_output="実際に動作する完成されたHTML/CSS/JSのコード",
    agent=coder,
    # ★自動保存はさせず、下のPython処理で綺麗にしてから保存するため、ここでは output_file を指定しません
)

# 3. チーム結成と実行
my_ai_company = Crew(
    agents=[pm, writer, coder],
    tasks=[task1, task2, task3],
    process=Process.sequential,
    verbose=True,
    max_rpm=15,
)

print("🤖 [社長AI] 本日の業務を開始します...")
result = my_ai_company.kickoff()

# ----------------------------------------------------------------
# ★【新機能】プログラマーが作ったコードから邪魔な「枠（```）」を切り落とす処理
# ----------------------------------------------------------------
print("🤖 [社長AI] プログラマーの成果物を検収し、余計なマークダウン枠を削除します...")
html_content = str(task3.output.raw)

# AIが「```html」や「```」を付けてしまった場合、その中身だけを抜き出す
if "```html" in html_content:
    html_content = html_content.split("```html")[1].split("```")[0]
elif "```" in html_content:
    html_content = html_content.split("```")[1].split("```")[0]

html_content = html_content.strip()

# 完全に綺麗なHTMLだけを「index.html」として保存する
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("🤖 [社長AI] 本日の業務がすべて完了しました！綺麗なアプリを納品します。")
