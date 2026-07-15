import os
import sys
import time
import subprocess
import atexit
from datetime import datetime, timedelta, timezone

# ==========================================================
# 🗝️ 多重起動防止（ロックファイル）管理
# ==========================================================
LOCK_FILE = ".loop.lock"

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        print(f"⚠️ [重複防止] 前回のループ処理がまだ実行中です。({LOCK_FILE} が存在します)")
        print("今回のジョブは多重起動を防ぐために安全に即時終了します。")
        sys.exit(0)
    
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    print(f"🔑 [ロック取得] ロックファイルを確保しました (PID: {os.getpid()})")

def release_lock():
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            print("🔓 [ロック解除] ロックファイルを削除しました。")
        except Exception as e:
            print(f"⚠️ ロックファイル削除失敗: {e}")

# エラー強制終了時も確実に鍵を返却する
atexit.register(release_lock)

# ==========================================================
# 🤖 メイン自律ループ処理
# ==========================================================
jst = timezone(timedelta(hours=9))
SCRIPTS_TO_RUN = ["main.py"]

# APIリミットセーフガード (1分間の最大リクエスト数12回：約5秒に1回の間隔)
MAX_REQUESTS_PER_MINUTE = 12
REQUEST_INTERVAL = 60 / MAX_REQUESTS_PER_MINUTE

def run_script_safely(script_path):
    if not os.path.exists(script_path):
        print(f"💡 スキップ: {script_path} はまだリポジトリ内に存在しません。")
        return False
        
    current_time = datetime.now(jst).strftime("%H:%M:%S")
    print(f"\n[🔄 AI R&Dループ実行] {current_time} - {script_path} を開始...")
    
    start_time = time.time()
    try:
        # pipで確実に入っている同一Python環境の仮想インタプリタで実行
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=300)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️ 実行ログ/エラー出力:\n{result.stderr}")
            
        elapsed = time.time() - start_time
        print(f"⏱️ 完了 (処理時間: {elapsed:.1f}秒)")
        
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
    # 5時間40分間、常時コンテナ内でループを実行
    max_loop_duration = 5 * 60 * 60 + 40 * 60 
    
    run_count = 0
    while True:
        elapsed_total = time.time() - loop_start_time
        if elapsed_total > max_loop_duration:
            print("⏳ コンテナ制限時間に達したため、次の巡回シフトへバトンを繋ぎます。")
            break
            
        run_count += 1
        print(f"\n--- 🤖 第 {run_count} 回目の AI Research 自律ループ ---")
        
        for script in SCRIPTS_TO_RUN:
            run_script_safely(script)
            
        time.sleep(15)
        
        # 成果物の自動コミット＆プッシュ処理
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
    acquire_lock()
    main()
