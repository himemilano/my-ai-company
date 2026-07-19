import os
import sys
import json
import glob
from datetime import datetime, timedelta, timezone

# --- ⚙️ タイムゾーンと日付の設定 ---
jst = timezone(timedelta(hours=9))
now = datetime.now(jst)
current_date = now.strftime("%Y-%m-%d")

print("🚀 [ai-company] 汎用型アプリ開発ギルド・メインエンジンを起動します...")

# 🛡️ 環境変数 'GEMINI_API_KEY' の存在チェック
if not os.environ.get("GEMINI_API_KEY"):
    print("\n❌ [致命的エラー] 環境変数 'GEMINI_API_KEY' が設定されていません！")
    sys.exit(1)

# 🎛️ プロジェクト切り替え盤の読み込み
if not os.path.exists("active_project.json"):
    print("❌ [環境エラー] ルートに active_project.json が見つかりません。")
    sys.exit(1)

with open("active_project.json", "r", encoding="utf-8") as f:
    proj_config = json.load(f)

# 📂 プロジェクトのルートパスを起点に、すべての内部フォルダを自動計算（完全隠蔽・カプセル化）
PROJECT_ROOT = proj_config["project_root"]
KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, "knowledge")
APP_DIR = os.path.join(PROJECT_ROOT, "geo_master_app")
LOG_DIR = os.path.join(PROJECT_ROOT, "outputs", "dev_logs")
STATE_FILE = os.path.join(LOG_DIR, "development_state.json")

os.makedirs(LOG_DIR, exist_ok=True)

# 📖 指定されたプロジェクトのknowledgeフォルダ内のみをスキャン
def load_project_knowledge_base():
    md_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md"))
    combined_context = ""
    loaded_count = 0
    
    print(f"📂 ターゲット [ {proj_config['project_title']} ] のナレッジをスキャン中...")
    
    for file_path in md_files:
        if "report" in file_path or "log" in file_path:
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                combined_context += f"\n\n=========================================\n"
                combined_context += f"📄 参照ファイル: {os.path.basename(file_path)}\n"
                combined_context += f"=========================================\n"
                combined_context += content
                loaded_count += 1
        except Exception as e:
            print(f"⚠️ ファイル {os.path.basename(file_path)} の読み込みに失敗: {e}")
            
    if not combined_context:
        return "プロジェクト固有のナレッジファイル（.md）が指定フォルダ内に見つかりませんでした。"
        
    print(f"✨ 計 {loaded_count} 個の専用ナレッジベースを正常にロードしました。")
    return combined_context

shared_knowledge_base = load_project_knowledge_base()

# 📋 開発ステータス（引き継ぎ帳）の動的管理
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "current_app": proj_config["project_title"],
        "status": "CODING_PHASE",
        "current_phase": "仕様書に基づく機能の順次実装フェーズ",
        "completed_features": [],
        "next_target_screen": "未定",
        "history": []
    }

state = load_state()

# 🔄 CrewAI最新環境用インポート
try:
    from crewai import Agent, Crew, Process, Task, LLM
    gemini_llm = LLM(model="gemini/gemini-2.5-flash", temperature=0.2)
except ImportError:
    from crewai import Agent, Crew, Process, Task
    from langchain_google_genai import ChatGoogleGenerativeAI
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# 💻 アプリ開発部のAIスペシャリスト
dev_pm = Agent(
    role="アプリ開発総括 PM 兼 COO",
    goal=f"支給された仕様書・専門ナレッジと既存コードを紐解き、{proj_config['project_title']} をストア申請に向けて着実に完成させる",
    backstory="プロジェクト全体の進捗を管理する敏腕マネージャー。無駄な推論ステップは省略し、結論を最短で出すリアリスト。エンジニアに本日の明確な1タスクを切り出すプロ。",
    verbose=True,
    llm=gemini_llm,
    max_rpm=3,
)

flutter_engineer = Agent(
    role="シニア Flutter/Dart 開発エンジニア",
    goal=f"PMの指示に基づき、{proj_config['project_title']} のソースコードや設定ファイルを拡張・修正・新規作成する",
    backstory="FlutterとDart言語の申し子。指示された専門ナレッジのエビデンスやロジックを、バグのないクリーンなコードとして完全に実装する技術者。",
    verbose=True,
    llm=gemini_llm,
    max_rpm=3,
)

store_qa_specialist = Agent(
    role="ストア申請 兼 QA（品質保証）責任者",
    goal="書かれたコードが仕様書および専門知識の要件を満たしているか、また将来的なストア審査を突破できる構成かを検証する",
    backstory="数々のアプリをストアに一発合格させてきた品質の鬼。専門用語ロジックの間違いや、不要な外部URLが含まれていないかを厳しくテストし、成果物を最終承認する砦。",
    verbose=True,
    llm=gemini_llm,
    max_rpm=3,
)

# 🚀 タスクの定義
task1 = Task(
    description=f"""
【最重要：開発対象アプリ】: {proj_config['project_title']}
【ソースコードおよび関連ファイル配置エリア】: {APP_DIR} 内のすべて
【専用ナレッジベース】:\n{shared_knowledge_base}

現在の開発ステート（{state['current_phase']}）および上記フォルダ内の既存コードを確認してください。
本日開発・修正すべき『具体的なFlutterの1画面、または1つのロジック』を厳選して決定し、エンジニアに {APP_DIR} 内のどのファイルをどう修正すべきか指示を出してください。
""",
    expected_output="本日の詳細な開発仕様指示書",
    agent=dev_pm
)

task2 = Task(
    description=f"PMの指示、および先述の仕様書・専門ナレッジの内容を基に、アプリに必要なDartコード等を正確に実装・修正してください。ファイルの書き出しや修正は必ず {APP_DIR} 内の適切な構造（lib/等）に対して行うこと。",
    expected_output="実装または修正されたDart/JSONコード一式（Markdownのコードブロック形式）",
    agent=flutter_engineer
)

task3 = Task(
    description=f"""
エンジニアが実装したコードをレビューし、仕様書や専門知識のロジック通りに作られているかチェックしてください。
最後に、次回の出勤メンバーへの『明日の引き継ぎ事項』をまとめてください。

⚠️【超重要：日付の厳守】
本日のリアルな日付は【 {current_date} 】です。
生成する「QA合格承認ログ」の承認日や、「明日への引き継ぎメモ」の日付には、過去のテンプレートの日付（2023年など）を決して使わず、必ず上記の【 {current_date} 】を正確に記載してください。
""",
    expected_output="本日の日付が正しく記載された、QA合格承認ログおよび明日への引き継ぎメモ",
    agent=store_qa_specialist
)

# 🌐 チーム結成と実行
dev_crew = Crew(
    agents=[dev_pm, flutter_engineer, store_qa_specialist],
    tasks=[task1, task2, task3],
    process=Process.sequential,
    verbose=True,
    max_rpm=4
)

print(f"\n📱 [ai-company] プロジェクト「{proj_config['project_title']}」の自律開発を開始します。")

try:
    result = dev_crew.kickoff()
    
    # 成果（本日の開発日報）の動的保存
    report_file = os.path.join(LOG_DIR, f"{current_date}_development_report.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(str(result))

    # ステートを更新して保存
    state["status"] = "CODING_PHASE"
    state["current_phase"] = "仕様書に基づく機能の順次実装フェーズ"
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

    print(f"🎉 💾 [ai-company] 業務が正常に完了しました。成果物: {report_file}")

except Exception as e:
    print(f"\n🚨 [緊急停止] Major Error または API制限が発生しました。: {e}")
    sys.exit(1)
