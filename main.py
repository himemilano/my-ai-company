import os
from crewai import Agent, Crew, Process, Task

# 1. エージェント（AI社員）の設定
pm = Agent(
    role="敏腕プロダクトマネージャー",
    goal="日常のちょっとした悩みを解決する、面白いWebアプリのアイデアを1つ考案する",
    backstory="あなたは数々のヒットアプリを生み出してきた天才PMです。斬新かつ、ブラウザだけで動くシンプルなアプリを考えるのが得意です。",
    verbose=True,
    llm="gemini/gemini-2.5-flash",  # 新しい爆速Geminiを使用
)

writer = Agent(
    role="テクニカルライター",
    goal="PMが出したアイデアを整理し、エンジニアがすぐ開発できるMarkdown仕様書を作成する",
    backstory="あなたは分かりやすく美しい構成で技術ドキュメントを書くプロフェッショナルです。",
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
    output_file="idea_of_the_day.md",  # この名前で自動保存されます
)

# 3. チーム結成と実行
my_ai_company = Crew(
    agents=[pm, writer],
    tasks=[task1, task2],
    process=Process.sequential,
    verbose=True,
)

print("🤖 [社長AI] 本日の業務を開始します...")
result = my_ai_company.kickoff()
print("🤖 [社長AI] 本日の業務が完了しました！仕様書を納品します。")
