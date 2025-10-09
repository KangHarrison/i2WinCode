from flask import Flask, request, jsonify
from plyer import notification
import pyperclip # 用于自动复制到剪贴板
import re        # 用于正则表达式提取验证码

app = Flask(__name__)

@app.route('/sms_code', methods=['POST'])
def receive_and_process_sms():
    """接收完整短信，提取验证码，复制到剪贴板，并发送通知。"""
    
    if not request.is_json:
        return jsonify({"status": "error", "message": "请求内容必须是 JSON 格式"}), 400

    data = request.json
    full_message = data.get('message', '未找到短信内容')
    
    print("-" * 50)
    print(f"[{request.remote_addr}] 收到完整短信内容:\n{full_message}")

    # --- 核心处理逻辑 ---
    
    # 1. 尝试提取验证码 (匹配 4 到 8 位连续数字)
    # 这是最常见和稳定的验证码正则模式。
    pattern = r'\d{4,8}' 
    match = re.search(pattern, full_message)
    
    if match:
        verification_code = match.group(0)
        
        # 2. 自动复制到剪贴板
        try:
            pyperclip.copy(verification_code)
            print(f"成功提取并复制到剪贴板: {verification_code}")
            
            # 3. 发送 Windows 通知
            notification.notify(
                title="✅ 验证码已复制",
                message=f"验证码: {verification_code}\n无需打开手机，直接粘贴即可。",
                app_name='SMS Verifier',
                timeout=10
            )
            
            return jsonify({
                "status": "success", 
                "message": "验证码已复制并通知", 
                "code": verification_code
            }), 200

        except Exception as e:
            # 如果复制失败 (例如 pyperclip 依赖问题)，仍然发送通知
            print(f"自动复制失败: {e}")
            notification.notify(
                title="⚠️ 验证码获取失败 (请查看终端)",
                message=full_message,
                app_name='SMS Verifier',
                timeout=10
            )
            return jsonify({"status": "error", "message": f"复制失败: {e}"}), 500

    else:
        # 未提取到验证码
        print("未提取到验证码，发送原始短信通知。")
        notification.notify(
            title="新短信通知",
            message=f"未能提取验证码，请查看原始短信内容。",
            app_name='SMS Verifier',
            timeout=10
        )
        return jsonify({"status": "warning", "message": "未提取到验证码"}), 200

if __name__ == '__main__':
    print("--- 启动本地短信接收服务 (终极便捷版) ---")
    print("运行中... 请勿关闭此终端。")
    app.run(host='0.0.0.0', port=5000)