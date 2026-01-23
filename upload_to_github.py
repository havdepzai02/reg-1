# upload_to_github.py - Upload data từ codespace lên GitHub
import os
import json
import base64
import requests
from datetime import datetime
import sys

def upload_accounts_data():
    """Upload file accounts-VN.json lên GitHub"""
    try:
        # Đường dẫn file thực tế
        data_file = "/home/codespace/SAJEEB-ERA/ACCOUNTS/accounts-VN.json"
        
        if not os.path.exists(data_file):
            print("❌ File accounts-VN.json không tìm thấy")
            return False
        
        # Đọc file
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Lấy GitHub Token từ environment variable
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            # Thử lấy từ file
            token_file = "/home/codespace/.github_token"
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    github_token = f.read().strip()
            else:
                print("❌ Không tìm thấy GitHub Token")
                return False
        
        # Lấy thông tin codespace
        codespace_name = os.getenv('CODESPACE_NAME', 'unknown-codespace')
        
        # Tạo filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"accounts_VN_{codespace_name}_{timestamp}.json"
        
        # Encode data
        content = json.dumps(data, indent=2, ensure_ascii=False)
        content_encoded = base64.b64encode(content.encode()).decode()
        
        # GitHub API headers
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Lấy username từ token
        user_response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if user_response.status_code != 200:
            print(f"❌ Không lấy được user info: {user_response.status_code}")
            return False
        
        username = user_response.json()['login']
        print(f"👤 GitHub user: {username}")
        
        # Repository để lưu data
        repo_name = "codespace-output"
        repo_full = f"{username}/{repo_name}"
        
        # Kiểm tra repository có tồn tại không
        repo_url = f"https://api.github.com/repos/{repo_full}"
        repo_response = requests.get(repo_url, headers=headers, timeout=10)
        
        if repo_response.status_code == 404:
            # Tạo repository mới
            print(f"📦 Tạo repository mới: {repo_name}")
            create_data = {
                "name": repo_name,
                "description": "Data output from codespaces",
                "private": True,
                "auto_init": True
            }
            create_response = requests.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json=create_data,
                timeout=10
            )
            
            if create_response.status_code != 201:
                print(f"❌ Không tạo được repository: {create_response.status_code}")
                return False
        
        # Upload file
        upload_url = f"https://api.github.com/repos/{repo_full}/contents/{filename}"
        
        upload_data = {
            "message": f"Auto-upload from {codespace_name}",
            "content": content_encoded,
            "branch": "main"
        }
        
        upload_response = requests.put(upload_url, headers=headers, json=upload_data, timeout=10)
        
        if upload_response.status_code == 201:
            print(f"✅ Đã upload thành công!")
            print(f"📁 Repository: {repo_full}")
            print(f"📄 File: {filename}")
            print(f"👤 Accounts: {len(data.get('accounts', []))}")
            print(f"💾 Size: {os.path.getsize(data_file) / 1024:.1f} KB")
            return True
        else:
            print(f"❌ Upload thất bại: {upload_response.status_code}")
            print(f"   Response: {upload_response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối: {e}")
        return False
    except Exception as e:
        print(f"❌ Lỗi: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    # Chạy standalone
    success = upload_accounts_data()
    sys.exit(0 if success else 1)
