import os
import sys
import time
import subprocess
from datetime import datetime, timedelta, timezone

# 日本時間設定
jst = timezone(timedelta(hours=9))

# 実行ターゲット：トップ階層にある実行スクリプト（お使いのファイル名に合わせて自由に変更可能です）
# デフォルトで一般的に使われる main.py や research.py などを順次自動実行する設定にしています。
SCRIPTS_TO_RUN = [
    "main.py",
    # "research.py", # もしトップ階層に他のスクリプトがあればコメントを外して追加可能
]

# APIリミットセーフガード (1分間の最大リクエスト数12回：約5秒に1回の間隔)
MAX_REQUESTS_PER_MINUTE = 12
REQUEST_INTERVAL = 60 / MAX_REQUESTS_PER_MINUTE

def run_script_safely(script_path):
    if not os.path.exists(script_path):
        print(f"💡 スキップ: {script_path} はまだリポジトリ内に存在しません。必要に応じてファイルを設置してください。")
        return False
        
    current_time = datetime.now(jst).strftime("%H:%M:%S")
    print(f"\n[🔄 AI R&Dループ実行] {current_time} - {script_path} を開始...")
    
    start_time = time.time()
    try:
        # プロセスとしてR&Dスクリプトを順次起動
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print(f"❌ エラー出力:\n{result.stderr}")
            
        elapsed = time.time() - start_time
        print(f"⏱️ 完了 (処理時間: {elapsed:.1f}秒)")
        
        # API保護待機
        time.sleep(REQUEST_INTERVAL)
        return True
    except subprocess.TimeoutExpired:
        print(f"⚠️ 5分以上応答がないためタイムアウトしました: {script_path}")
        return False
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        return False

def main():
    print("==========================================================")
    print("🔥 my-ai-company AI R&D 自律常時限界ループランナー 🔥")
    print("==========================================================")
    
    loop_start_time = time.time()
    max_loop_duration = 5 * 60 * 60 + 40 * 60 # 5時間40分間、常時コンテナ内でループを実行
    
    run_count = 0
    while True:
        elapsed_total = time.time() - loop_start_time
        if elapsed_total > max_loop_duration:
            print("⏳ コンテナ制限時間に達したため、次の巡回シフトへバトンを繋ぎます。")
            break
            
        run_count += 1
        print(f"\n--- 🤖 第 {run_count} 回目の AI Research 自律ループ ---")
        
        # 登録スクリプトを順に実行
        for script in SCRIPTS_TO_RUN:
            run_script_safely(script)
            
        # 1サイクル完了ごとに15秒待機
        time.sleep(15)
        
        # 生成された研究結果のレポートや分析ファイルを自動で検知してGitHubへプッシュ
        try:
            subprocess.run(["git", "config", "--local", "user.email", "action@github.com"], capture_output=True)
            subprocess.run(["git", "config", "--local", "user.name", "GitHub Action"], capture_output=True)
            subprocess.run(["git", "add", "."], capture_output=True)
            
            status_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if status_res.stdout.strip():
                print("📦 新規研究成果物の作成を検知！自動でコミット・プッシュします...")
                subprocess.run(["git", "commit", "-m", "🤖 [AI-Research] 24時間自律ループにより最新R&Dレポートを自動プッシュ"], capture_output=True)
                subprocess.run(["git", "push"], capture_output=True)
        except Exception as e:
            print(f"⚠️ 自動コミット例外: {e}")

if __name__ == "__main__":
    main()

