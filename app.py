#!/usr/bin/env python3
"""
ClickUp + Infobip WhatsApp - Complete 2-Way Integration
Send messages + Receive responses + Web Dashboard
"""

from flask import Flask, request, jsonify, render_template_string
import requests
import json
from datetime import datetime, timedelta
import sqlite3
import threading
from threading import Thread
import time

app = Flask(__name__)

# Credentials
CLICKUP_API_KEY = "pk_182698591_O1HWVO7Z9TM1KRC8ILCQLNPJ3IXWAP5P"
CLICKUP_API = "https://api.clickup.com/api/v2"

INFOBIP_API_KEY = "7a3d30a4798c18a1054edfd356ca0ca6-ed5080d0-4b51-4b34-9817-35b94cc8982f"
INFOBIP_API = "https://8v45x1.api.infobip.com"
WHATSAPP_SENDER = "+44 7860 088970"

TEAM_ID = "90151068705"
SPACE_ID = "90157253012"

# Database setup
def init_db():
    """Initialize SQLite database for conversations"""
    conn = sqlite3.connect('/tmp/whatsapp_messages.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id TEXT PRIMARY KEY, 
                  direction TEXT,
                  phone TEXT, 
                  message TEXT, 
                  timestamp DATETIME,
                  task_id TEXT,
                  status TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (phone TEXT PRIMARY KEY,
                  name TEXT,
                  last_message DATETIME,
                  task_id TEXT)''')
    
    conn.commit()
    conn.close()

def store_message(direction, phone, message, task_id=None):
    """Store message in database"""
    conn = sqlite3.connect('/tmp/whatsapp_messages.db')
    c = conn.cursor()
    
    msg_id = f"{phone}_{datetime.now().timestamp()}"
    
    c.execute('''INSERT INTO messages 
                 (id, direction, phone, message, timestamp, task_id, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (msg_id, direction, phone, message, datetime.now(), task_id, "sent" if direction == "out" else "received"))
    
    conn.commit()
    conn.close()
    
    return msg_id

def get_conversations():
    """Get all conversations"""
    conn = sqlite3.connect('/tmp/whatsapp_messages.db')
    c = conn.cursor()
    
    c.execute('''SELECT DISTINCT phone FROM messages ORDER BY timestamp DESC''')
    phones = [row[0] for row in c.fetchall()]
    
    conversations = {}
    for phone in phones:
        c.execute('''SELECT * FROM messages WHERE phone = ? ORDER BY timestamp DESC LIMIT 50''', (phone,))
        messages = c.fetchall()
        conversations[phone] = messages
    
    conn.close()
    return conversations

# ClickUp Integration
def get_all_tasks():
    """Get all tasks from ClickUp"""
    try:
        url = f"{CLICKUP_API}/team/{TEAM_ID}/task"
        headers = {"Authorization": CLICKUP_API_KEY}
        
        response = requests.get(url, headers=headers, params={"include_closed": "false"})
        tasks = response.json().get("tasks", [])
        
        print(f"✅ Found {len(tasks)} tasks")
        return tasks
    
    except Exception as e:
        print(f"❌ Error fetching tasks: {e}")
        return []

def check_expiring_soon(tasks, days_before=1):
    """Find tasks expiring in next N days"""
    expiring = []
    now = datetime.now()
    deadline = now + timedelta(days=days_before)
    
    for task in tasks:
        if task.get("due_date"):
            due_timestamp = int(task["due_date"]) / 1000
            due_date = datetime.fromtimestamp(due_timestamp)
            
            if now < due_date <= deadline:
                expiring.append({
                    "id": task["id"],
                    "name": task["name"],
                    "due_date": due_date,
                    "custom_fields": task.get("custom_fields", []),
                    "assignees": task.get("assignees", [])
                })
    
    return expiring

def extract_whatsapp_number(task):
    """Extract WhatsApp number from custom fields"""
    for field in task.get("custom_fields", []):
        if "whatsapp" in field.get("name", "").lower():
            return field.get("value")
    return None

def extract_client_name(task):
    """Extract client name"""
    for field in task.get("custom_fields", []):
        if "client" in field.get("name", "").lower():
            return field.get("value")
    return task.get("name", "Valued Client")

# Infobip WhatsApp
def send_whatsapp_message(to_number, message, task_id=None):
    """Send WhatsApp message via Infobip"""
    try:
        url = f"{INFOBIP_API}/whatsapp/1/message/send"
        
        headers = {
            "Authorization": f"App {INFOBIP_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Clean phone number
        clean_phone = to_number.replace(" ", "").replace("-", "").replace("+", "")
        if not clean_phone.startswith("44"):
            clean_phone = "44" + clean_phone.lstrip("0")
        
        payload = {
            "messages": [
                {
                    "from": "WhatsApp",
                    "to": clean_phone,
                    "messageType": "TEXT",
                    "text": message
                }
            ]
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"✅ WhatsApp sent to {to_number}")
            store_message("out", to_number, message, task_id)
            return True
        else:
            print(f"❌ WhatsApp failed: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error sending WhatsApp: {e}")
        return False

def generate_message(client_name, due_date, task_name):
    """Generate WhatsApp message"""
    due_str = due_date.strftime("%d %b %Y")
    
    message = f"""Salut {client_name},

Aceasta este o reamintire că abonamentul tău expiră pe {due_str}.

📋 Task: {task_name}

Pentru reînnoire sau întrebări, contactează-ne.

Mulțumim!
Neo-Boost Team"""
    
    return message

# Automation
def run_automation():
    """Main automation loop"""
    print("🤖 Automation Started")
    
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking tasks...")
            
            tasks = get_all_tasks()
            expiring = check_expiring_soon(tasks, days_before=1)
            
            if expiring:
                print(f"⚠️ Found {len(expiring)} expiring tasks")
                
                for task in expiring:
                    whatsapp = extract_whatsapp_number(task)
                    client = extract_client_name(task)
                    
                    if whatsapp:
                        message = generate_message(client, task["due_date"], task["name"])
                        print(f"📱 Sending to {whatsapp}")
                        send_whatsapp_message(whatsapp, message, task["id"])
                    else:
                        print(f"⚠️ No WhatsApp for {task['name']}")
            else:
                print("✅ No expiring tasks")
            
            time.sleep(86400)  # 24 hours
        
        except Exception as e:
            print(f"❌ Automation error: {e}")
            time.sleep(60)

# Flask Routes
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Receive WhatsApp messages from Infobip"""
    try:
        data = request.json
        
        # Parse Infobip webhook
        if 'results' in data:
            for result in data['results']:
                phone = result.get('from')
                message = result.get('text', {}).get('body', '')
                
                print(f"📨 Received from {phone}: {message}")
                
                # Store message
                store_message("in", phone, message)
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Web dashboard for conversations"""
    conversations = get_conversations()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp Dashboard</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .messages { background: white; padding: 20px; border-radius: 8px; }
            .message { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .out { background: #dcf8c6; text-align: right; }
            .in { background: #e3e3e3; }
            .timestamp { font-size: 12px; color: #999; }
            h2 { color: #333; }
            .phone { font-weight: bold; color: #0084ff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 WhatsApp Conversations</h1>
            <div class="messages">
    """
    
    for phone, messages in conversations.items():
        html += f"<h2><span class='phone'>{phone}</span></h2>"
        for msg in reversed(messages):
            direction = msg[1]
            text = msg[3]
            timestamp = msg[4]
            
            html += f"""
            <div class="message {direction}">
                <div>{text}</div>
                <div class="timestamp">{timestamp}</div>
            </div>
            """
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html)

@app.route('/send', methods=['POST'])
def send_manual():
    """Manually send WhatsApp message"""
    data = request.json
    phone = data.get('phone')
    message = data.get('message')
    
    if send_whatsapp_message(phone, message):
        return jsonify({"status": "sent"}), 200
    else:
        return jsonify({"error": "Failed to send"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Start automation thread
    automation_thread = Thread(target=run_automation, daemon=True)
    automation_thread.start()
    
    print("✅ WhatsApp Automation Started")
    print("🌐 Dashboard: http://localhost:7777/dashboard")
    print("🪝 Webhook: http://localhost:7777/webhook/whatsapp")
    
    app.run(host='0.0.0.0', port=7777, debug=False)
