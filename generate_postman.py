import os
import yaml

base_dir = r"E:\Robe\robe-backend\postman\collections\RoBe Backend API"

# Helper function to write yaml
def write_req(folder, name, method, url, body_content=None):
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
    data = {
        "$kind": "http-request",
        "name": name,
        "method": method,
        "url": url,
        "headers": [
            {"key": "Authorization", "value": "Bearer {{access_token}}"}
        ]
    }
    
    if body_content:
        data["headers"].append({"key": "Content-Type", "value": "application/json"})
        data["body"] = {
            "type": "json",
            "content": body_content
        }
        
    file_path = os.path.join(base_dir, folder, f"{name}.request.yaml")
    with open(file_path, "w") as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)

# 05 - Chat
write_req("05 - Chat", "Start Session", "POST", "{{base_url}}/chat/sessions", "{\n  \"topic_id\": \"{{topic_id}}\"\n}")
write_req("05 - Chat", "Get Session", "GET", "{{base_url}}/chat/sessions/{{session_id}}")
write_req("05 - Chat", "Get Session Messages", "GET", "{{base_url}}/chat/sessions/{{session_id}}/messages")
write_req("05 - Chat", "Send Message", "POST", "{{base_url}}/chat/sessions/{{session_id}}/messages", "{\n  \"message_text\": \"Hi there, what should I feed my new kitten?\"\n}")
