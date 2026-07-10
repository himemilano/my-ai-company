
import os
import json
from datetime import datetime, timedelta, timezone
from crewai import Agent, Crew, Process, Task

# --- ⚙️ タイムゾーンと日付の設定 ---
jst = timezone(timedelta(hours=9))
now = datetime.now(jst)
current_date = now.strftime("%Y-%m-%d")

# フォルダの作成
os.makedirs("outputs/dev_logs", exist_ok=True)
STATE_FILE = "outputs/dev_logs/development_state.json"

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
        "next_target_screen": "未定（初回分析後に決定）",
        "history": []
    }

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

state = load_state()

# --- 💻 アプリ開発部のAIスペシャリスト（エージェント定義） ---

dev_pm = Agent(
    role="アプリ開発総括 PM 兼 COO",
    goal="アップロードされた仕様書(.md)と既存のDartコードを読み解き、ストア申請に向けて毎日1つずつ確実に機能を完成させる",
    backstory="プロジェクト全体の進捗（バックログ）を管理する冷徹なマネージャー。Geminiの無料枠を意識し、一度に多くの開発を詰め込まず、今日の開発目標を1つに絞り込むプロ。",
    verbose=True,
    llm="gemini/gemini-2.5-flash",
)

flutter_engineer = Agent(
    role="シニア Flutter/Dart 開発エンジニア",
    goal="PMの指示に基づき、地質調査技士アプリの.dartファイルや.json設定ファイルを拡張・修正・新規作成する",
    backstory="FlutterとDart言語の申し子。マテリアルデザインに精通し、国家資格の過去問データやポケットブックの知識をクリーンなソースコードとして実装する技術者。",
    verbose=True,
    llm="gemini/gemini-2.5-flash",
)

store_qa_specialist = Agent(
    role="ストア申請 兼 QA（品質保証）責任者",
    goal="書かれたコードに致命的なバグがないか、またApple/Googleのストア審査（ガイドライン）を突破できる構成かを検証する",
    backstory="数々のアプリを両OSのストアに一発合格させてきた伝説のQA。ユーザーが使いやすいか、規約違反がないかを厳しくテストし、本日の成果物を最終承認する砦。",
    verbose=True,
    llm="gemini/gemini-2.5-flash",
)

# --- 🚀 開発フェーズに応じたタスクの自動生成 ---
tasks = []

# リポジトリ内の情報をAIに教えるための簡易コンテキスト
spec_info = "リポジトリ内にある、会長がアップロードした仕様書(.mdファイル)を最優先で確認してください。"

task1 = Task(
    description=f"{spec_info} 現在の開発ステート（{state['current_phase']}）を確認し、本日開発・修正すべき『具体的なFlutterの1画面、または1機能』を決定してください。",
    expected_output="本日の開発仕様指示書",
    agent=dev_pm
)

task2 = Task(
    description="PMの指示とアップロード済みの既存コードを確認し、地質調査技士アプリに必要なDartコード（またはJSON等の設定）を実装・修正してください。コードは省略せず、再利用可能な形で記述すること。",
    expected_output="実装または修正されたDart/JSONコード一式",
    agent=flutter_engineer
)

task3 = Task(
    description="実装されたコードをレビューし、構図の破綻がないか、将来的なiOS/Androidのストア申請規約（App Store Reviewガイドライン等）に準拠しているか品質チェックを行ってください。また、次回の出勤メンバーへの『明日の引き継ぎ事項』をまとめてください。",
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
    max_rpm=10  # 🔥 Gemini無料枠（15RPM）を絶対に突破しない安全ブレーキ
)

print(f"📱 [ai-company] {state['current_app']} の自律開発を開始します。現在のフェーズ: {state['current_phase']}")
result = dev_crew.kickoff()

# 成果（本日の開発日報・コードスニペット）の保存
log_folder = "outputs/dev_logs"
report_file = f"{log_folder}/{current_date}_development_report.md"

with open(report_file, "w", encoding="utf-8") as f:
    f.write(str(result))

# 次回に向けてステートを更新（モック更新：実際はAIの出力を元にPMが次回フェーズを決定するよう促す）
state["status"] = "CODING_PHASE"
state["current_phase"] = "仕様書に基づく機能の順次実装フェーズ"
save_state(state)

print(f"💾 [ai-company] 今日の業務が完了しました。成果物: {report_file}")
