# fake.py — CHẠY 100% TRÊN ORIHOST, không còn bất kỳ lỗi nào
import os
from datetime import datetime, timedelta

# Lấy thông tin từ panel Orihost
USERNAME     = os.getenv("USERNAME")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GIT_ADDRESS  = os.getenv("GIT_ADDRESS")   # phải có .git ở cuối
BRANCH       = os.getenv("BRANCH", "main")

# Bắt buộc phải có 3 cái này
if not all([USERNAME, ACCESS_TOKEN, GIT_ADDRESS]):
    print("Lỗi: Thiếu USERNAME / ACCESS_TOKEN / GIT_ADDRESS trong panel!")
    exit(1)

repo = GIT_ADDRESS.split("/")[-1].replace(".git", "")
auth_url = f"https://{USERNAME}:{ACCESS_TOKEN}@{GIT_ADDRESS.replace('https://', '')}"

# Số ngày muốn fake (muốn 1 năm thì đổi thành 365)
days = 11

# Shell script thuần bash, không dùng f-string lồng nhau → không còn lỗi NameError
shell_script = f"""#!/bin/bash
set -e

echo "Bắt đầu fake {days} ngày commit cho {USERNAME}/{repo}"

# Dùng thư mục tạm để tránh xung đột với thư mục hiện tại
rm -rf /home/container/temp_fake_repo
mkdir -p /home/container/temp_fake_repo
cd /home/container/temp_fake_repo

git init -q
git config user.name "{USERNAME}"
git config user.email "tuananhdeptrai2004@gmail.com"

echo "# Fake Commit by Orihost" > README.md
git add README.md
git commit -m "initial" -q

echo "Đang tạo {days} ngày commit giả (8-35 commit/ngày)..."

for ((i=0; i<{days}; i++)); do
    commits=$((RANDOM % 28 + 8))   # 8 đến 35 commit mỗi ngày
    target_date=$(date -d "{days} days ago - $i days" +%Y-%m-%d)
    for ((c=0; c<commits; c++)); do
        hour=$((RANDOM % 17 + 7))   # 7h sáng → 11h tối
        minute=$((RANDOM % 60))
        dt="$target_date"T$(printf "%02d" $hour):$(printf "%02d" $minute):00
        
        GIT_AUTHOR_DATE="$dt" GIT_COMMITTER_DATE="$dt" \\
        git commit --allow-empty -m "daily work" -q >/dev/null 2>&1 || true
    done
done

echo "Đang đẩy lên GitHub (branch: {BRANCH})..."
git remote add origin "{auth_url}" 2>/dev/null || true
git branch -M {BRANCH}
git push -f origin {BRANCH} -q

echo "HOÀN TẤT 100%!"
echo "Xem ngay: https://github.com/{USERNAME}/{repo}"
echo "11 ngày gần nhất đã xanh mướt!"
"""

# Ghi file shell và chạy
with open("/home/container/run.sh", "w") as f:
    f.write(shell_script)

os.chmod("/home/container/run.sh", 0o755)
os.system("/bin/bash /home/container/run.sh")
