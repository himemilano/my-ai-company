import os
import json
import glob
from datetime import datetime, timedelta, timezone
# 🔥 LangChainを捨て、CrewAIネイティブの LLM クラスをインポート
from crewai import Agent, Crew, Process, Task, LLM

# --- ⚙️ タイムゾーンと日付の設定 ---
jst = timezone(timedelta(hours=9))
now = datetime.now(jst)
current_date = now.strftime("%Y-%m-%d")

# フォルダの作成
os.makedirs("outputs/dev_logs", exist_ok=True)
STATE_FILE = "outputs/dev_logs/development_state.json"

# --- 📖 リポジトリ内のマークダウンファイル（仕様書・知識）を物理的に読み込む ---
def load_all_markdown_contexts():
    md_files = glob.glob("*.md")
    combined_context = ""
    
    for file_path in md_files:
        # ログファイルなどは除外
        if "report" in file_path or "log" in file_path:
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                combined_context += f"\n\n=========================================\n"
                combined_context += f"📄 参照ファイル: {file_path}\n"
                combined_context += f"=========================================\n"
                combined_context += content
        except Exception as e:
            print(f"⚠️ ファイル {file_path} の読み込みに失敗しました: {e}")
            
    if not combined_context:
        return "リポジトリ内に読み込める仕様書や知識の.mdファイルが見つかりませんでした。"
    return combined_context

# 仕様書やナレッジの中身をロード
shared_knowledge_base = load_all_markdown_contexts()

# --- 📋 開発ステータス（引き継ぎ帳）の管理 ---
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "current_app": "地質調査技士試験対策アプリ",
        "status": "ANALYZING_EXISTING_CODE",
        "current_phase": "前任者のDartコードと仕様書の分析",
        "completed_features": [],
        "next_target_screen": "未定",
        "history": []
    }

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

state = load_state()


# --- 🛡️ CrewAI公式ネイティブ LLM 定義（Pydanticエラー完全回避型） ---
# モデル名に `gemini/` 接頭辞をつけることで、型エラーを防ぎつつ、内部で安全に最適稼働します。
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.3,       # アプリ開発・コード生成の正確性を高めるため、ランダム性を抑えめに調整
)


# --- 💻 アプリ開発部のAIスペシャリスト（エージェント定義） ---
# 各エージェントにエラーの出ない gemini_llm を配備し、個別速度を厳しく制限

dev_pm = Agent(
    role="アプリ開発総括 PM 兼 COO",
    goal="インプットされた仕様書と既存のDartコードを紐解き、ストア申請に向けて毎日1つずつ確実に機能を完成させる",
    backstory="プロジェクト全体の進捗を管理する敏腕マネージャー。提供された仕様書や専門知識のテキストを熟読し、本日開発すべき最優先タスクを1つに絞り込むプロ。",
    verbose=True,
    llm=gemini_llm,        # 🔓 ネイティブLLMをセット
    max_rpm=3,             # 🔥 個別リクエスト数を1分間3回に制限（安全圏）
)

flutter_engineer = Agent(
    role="シニア Flutter/Dart 開発エンジニア",
    goal="PMの指示に基づき、地質調査技士アプリの.dartファイルや.json設定ファイルを拡張・修正・新規作成する",
    backstory="FlutterとDart言語の申し子。仕様書に記載された機能や、ボーリングポケットブックの専門ナレッジを、バグのないクリーンなソースコードとしてガシガシ実装する技術者。",
    verbose=True,
    llm=gemini_llm,        # 🔓 ネイティブLLMをセット
    max_rpm=3,             # 🔥 個別リクエスト数を1分間3回に制限
)

store_qa_specialist = Agent(
    role="ストア申請 兼 QA（品質保証）責任者",
    goal="書かれたコードが仕様書および専門知識の要件を満たしているか、またApple/Googleのストア審査を突破できる構成かを検証する",
    backstory="数々のアプリをストアに一発合格させてきた品質の鬼。専門用語のロジックに間違いがないか、規約違反がないかを厳しくテストし、本日の成果物を最終承認する砦。",
    verbose=True,
    llm=gemini_llm,        # 🔓 ネイティブLLMをセット
    max_rpm=3,             # 🔥 個別リクエスト数を1分間3回に制限
)

# --- 🚀 タスクの定義（インプットされた仕様書・知識を直接埋め込む） ---

task1 = Task(
    description=f"""
【最重要：会長から支給された仕様書および専門ナレッジ】
{shared_knowledge_base}

上記の仕様書、およびリポジトリ内にある既存のDartコードを確認してください。
現在の開発ステート（{state['current_phase']}）を踏まえ、本日開発・修正すべき『具体的なFlutterの1画面、または1つのバックエンドロジック』を厳選して決定し、エンジニアに指示を出してください。
""",
    expected_output="本日の詳細な開発仕様指示書",
    agent=dev_pm
)

task2 = Task(
    description="PMの指示、および先述の仕様書・専門ナレッジの内容を基に、地質調査技士アプリに必要なDartコード（またはJSON等の設定）を正確に実装・修正してください。コードは省略せず、完全に動作する形で記述すること。",
    expected_output="実装または修正されたDart/JSONコード一式（Markdownのコードブロック形式）",
    agent=flutter_engineer
)

task3 = Task(
    description="エンジニアが実装したコードをレビューし、仕様書や専門知識のロジック通りに作られているか、また将来的なストア申請規約に準拠しているかチェックしてください。最後に、次回の出勤メンバーへの『明日の引き継ぎ事項』をまとめてください。",
    expected_output="QA合格承認ログおよび明日への引き継ぎメモ",
    agent=store_qa_specialist
)

tasks = [task1, task2, task3]

# --- 🌐 チーム結成と実行（Gemini無料枠セーフティ完備） ---
dev_crew = Crew(
    agents=[dev_pm, flutter_engineer, store_qa_specialist],
    tasks=tasks,
    process=Process.sequential,
    verbose=True,
    max_rpm=4  # 🔥 クルー全体での1分間リクエスト数を4回に制限
)

print(f"📱 [ai-company] {state['current_app']} の自律開発を開始します。")
result = dev_crew.kickoff()

# 成果（本日の開発日報・コードスニペット）の保存
log_folder = "outputs/dev_logs"
report_file = f"{log_folder}/{current_date}_development_report.md"

with open(report_file, "w", encoding="utf-8") as f:
    f.write(str(result))

# 次回に向けてステートを更新
state["status"] = "CODING_PHASE"
state["current_phase"] = "仕様書に基づく機能の順次実装フェーズ"
save_state(state)

print(f"💾 [ai-company] 本日の業務が完了しました。成果物: {report_file}")
