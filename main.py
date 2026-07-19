import os
import sys
import json
import glob
from datetime import datetime, timedelta, timezone
# CrewAIネイティブの LLM クラスをインポート
from crewai import Agent, Crew, Process, Task, LLM

# --- ⚙️ タイムゾーンと日付の設定 ---
jst = timezone(timedelta(hours=9))
now = datetime.now(jst)
current_date = now.strftime("%Y-%m-%d")

# 📂 フォルダの作成
os.makedirs("outputs/dev_logs", exist_ok=True)
STATE_FILE = "outputs/dev_logs/development_state.json"

print("🚀 [ai-company] 地質調査技士アプリ・統括システム（社長）を起動します...")

# 🛡️ 【最終防衛ライン】環境変数 'GEMINI_API_KEY' の存在チェック
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("\n❌ [社長の激怒] 環境変数 'GEMINI_API_KEY' が設定されていません！")
    print("GitHub ActionsのSecrets、またはローカルの環境変数を確認してください。")
    print("安全のため、全マシーンの稼働を強制停止します。")
    sys.exit(1) # 終了コード1を出し、Actions側の無限ループをここで完全遮断する

# --- 📖 リポジトリ内のマークダウンファイル（仕様書・NotebookLM抽出ナレッジ）を物理的に読み込む ---
def load_all_markdown_contexts():
    md_files = glob.glob("*.md")
    combined_context = ""
    loaded_count = 0
    
    print(f"📂 ナレッジベースをスキャン中... 発見された.mdファイル: {len(md_files)}個")
    
    for file_path in md_files:
        # ログファイルや成果物レポートなどは除外して純粋なナレッジだけを抽出
        if "report" in file_path or "log" in file_path:
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                combined_context += f"\n\n=========================================\n"
                combined_context += f"📄 参照ファイル: {file_path}\n"
                combined_context += f"=========================================\n"
                combined_context += content
                loaded_count += 1
        except Exception as e:
            print(f"⚠️ ファイル {file_path} の読み込みに失敗しました: {e}")
            
    if not combined_context:
        return "リポジトリ内に読み込める仕様書や知識の.mdファイルが見つかりませんでした。"
        
    print(f"✨ 計 {loaded_count} 個の特大ナレッジベース（NotebookLM抽出データ）を脳内に正常にロードしました。")
    return combined_context

# 仕様書やナレッジの中身をロード（宝の山を完全同期）
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

# --- 🛡️ CrewAI公式ネイティブ LLM 定義 ---
# 2026年最新の超高知能・広コンテキストモデル 'gemini-2.5-flash' を指定
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.2,       # 正確な工学的エビデンスを出力させるため、ランダム性をさらに抑えめに調整
)

# --- 💻 アプリ開発部のAIスペシャリスト（エージェント定義） ---
# 巨大なナレッジを処理する際、無駄な思考ループで429(TPM制限)を起こさないようセーフティ指示を背後に埋め込み

dev_pm = Agent(
    role="アプリ開発総括 PM 兼 COO",
    goal="インプットされた大量の仕様書・ポケットブック知識と既存のDartコードを紐解き、ストア申請に向けて毎日1つずつ確実に機能を完成させる",
    backstory="プロジェクト全体の進捗を管理する敏腕マネージャー。支給された膨大な専門知識テキストを瞬時に参照し、本日開発すべき最優先タスクを1つに絞り込むプロ。無駄な推論ステップは省略し、結論を最短で出すリアリスト。",
    verbose=True,
    llm=gemini_llm,
    max_rpm=3,             # 1分間のリクエスト数を制限し、セーフティを担保
)

flutter_engineer = Agent(
    role="シニア Flutter/Dart 開発エンジニア",
    goal="PMの指示に基づき、地質調査技士アプリの.dartファイルや.json設定ファイルを拡張・修正・新規作成する",
    backstory="FlutterとDart言語の申し子。ボーリングポケットブックの専門ナレッジ（掘進理論やLLT試験の測定原理など）を、バグのないクリーンなソースコードとしてガシガシ実装する技術者。指示された知識ベースに書かれた工学的エビデンスをそのままコード内の解説文に反映させる天才。",
    verbose=True,
    llm=gemini_llm,
    max_rpm=3,
)

store_qa_specialist = Agent(
    role="ストア申請 兼 QA（品質保証）責任者",
    goal="書かれたコードが仕様書および専門知識の要件を満たしているか、またApple/Googleのストア審査を突破できる構成かを検証する",
    backstory="数々のアプリをストアに一発合格させてきた品質の鬼。専門用語のタップポップアップ機能のロジックや、解説文に外部URLが含まれていないかを厳しくテストし、本日の成果物を最終承認する砦。",
    verbose=True,
    llm=gemini_llm,
    max_rpm=3,
)

# --- 🚀 タスクの定義 ---
# コンテキストが巨大なため、エージェントが迷子にならないよう「フォーカスすべきルール」を明文化

task1 = Task(
    description=f"""
【最重要：会長から支給された仕様書および専門ナレッジ】
{shared_knowledge_base}

上記の膨大なナレッジ（ボーリングポケットブックのエビデンス）、およびリポジトリ内にある既存のDartコードを確認してください。
現在の開発ステート（{state['current_phase']}）を踏まえ、本日開発・修正すべき『具体的なFlutterの1画面、または1つのバックエンドロジック（例：図解付き過去問演習ユニットの土台、または用語タップポップアップ機能）』を厳選して決定し、エンジニアに指示を出してください。
※外部URLは一切使用せず、必ず上記ナレッジ内の工学的エビデンス（掘進の3条件など）をベースにすること。
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
    max_rpm=4  # クルー全体での1分間リクエスト数を4回に制限（無料枠のTPM/RPM枯渇を徹底防衛）
)

print(f"\n📱 [ai-company] {state['current_app']} の自律開発を開始します。")

try:
    # 🚀 エージェントたちのリレーを開始
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

    print(f"🎉 💾 [ai-company] 本日の業務が正常に完了しました。成果物: {report_file}")

except Exception as e:
    print(f"\n🚨 [緊急停止] エージェントの稼働中に重大なエラー、またはAPI制限(429/404)が発生しました。")
    print(f"詳細エラー: {e}")
    print("これ以上のトークン浪費とデプロイ崩壊を防ぐため、ここで処理を安全に緊急停止します。")
    sys.exit(1) # 💥 終了コード1を出し、GitHub Actions側の自動ループ・二次災害を即座にストップさせる
