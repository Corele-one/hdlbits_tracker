#!/usr/bin/env python3
import json
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(".hdlbits_tracker")
DATA_FILE = DATA_DIR / "data.json"
PLAN_FILE = DATA_DIR / "plan.json"

DEFAULT_PLAN = {
    "start_date": datetime.now().strftime("%Y-%m-%d"),
    "daily_goal": 2,
    "phases": [
        {"name": "Phase 1: 基础", "weeks": 3, "total": 35, "color": "#4CAF50"},
        {"name": "Phase 2: 组合", "weeks": 4, "total": 35, "color": "#FF9800"},
        {"name": "Phase 3: 时序", "weeks": 4, "total": 30, "color": "#2196F3"},
        {"name": "Phase 4: FSM", "weeks": 4, "total": 35, "color": "#F44336"},
        {"name": "Phase 5: 综合", "weeks": 3, "total": 30, "color": "#9C27B0"}
    ]
}

def init():
    DATA_DIR.mkdir(exist_ok=True)
    if not PLAN_FILE.exists():
        with open(PLAN_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PLAN, f, indent=2)
    if not DATA_FILE.exists():
        data = {"start_date": DEFAULT_PLAN["start_date"], "daily": []}
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    print("✅ 初始化完成")

def add(count, problems=None, note=None):
    """记录今日进度（自动合并同一天记录）"""
    data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    plan = json.loads(PLAN_FILE.read_text(encoding='utf-8'))
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 计算当前阶段
    start = datetime.strptime(plan["start_date"], "%Y-%m-%d")
    days = (datetime.now() - start).days
    current_phase = plan["phases"][0]["name"]
    week = 0
    for p in plan["phases"]:
        week += p["weeks"]
        if days < week * 7:
            current_phase = p["name"]
            break
    
    # 检查是否已有今日记录
    existing_idx = None
    for i, d in enumerate(data["daily"]):
        if d["date"] == today:
            existing_idx = i
            break
    
    if existing_idx is not None:
        # 合并到已有记录
        old = data["daily"][existing_idx]
        old["done"] += count
        old["planned"] = plan["daily_goal"]
        if problems:
            old["problems"].extend(problems)
        if note:
            if old["note"]:
                old["note"] += "; " + note
            else:
                old["note"] = note
        
        # 更新阶段（以防跨阶段）
        old["phase"] = current_phase
        
        status = "✅" if old["done"] >= old["planned"] else "⚠️"
        print(f"{status} 追加成功: {today} - 累计完成 {old['done']}/{old['planned']} 题 ({current_phase})")
        if problems:
            print(f"   题目: {', '.join(problems)}")
    else:
        # 创建新记录
        entry = {
            "date": today,
            "done": count,
            "planned": plan["daily_goal"],
            "phase": current_phase,
            "problems": problems or [],
            "note": note or ""
        }
        data["daily"].append(entry)
        
        status = "✅" if count >= plan["daily_goal"] else "⚠️"
        print(f"{status} 记录成功: {today} - {count}题 ({current_phase})")
    
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # 自动导出Notion（如果配置了）
    if os.path.exists("notion_config.json"):
        try:
            sync_notion(data["daily"][-1])
        except Exception as e:
            print(f"Notion同步失败（可忽略）: {e}")

def sync_notion(entry):
    """同步到Notion（Step 5配置后生效）"""
    import requests
    config = json.loads(Path("notion_config.json").read_text())
    
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {"database_id": config["database_id"]},
        "properties": {
            "Date": {"date": {"start": entry["date"]}},
            "Count": {"number": entry["done"]},
            "Problems": {"multi_select": [{"name": p} for p in entry["problems"]]},
            "Phase": {"select": {"name": entry["phase"]}},
            "Status": {"checkbox": entry["done"] >= entry["planned"]}
        }
    }
    
    requests.post(url, headers=headers, json=data)

def show():
    """终端显示简易进度"""
    data = json.loads(DATA_FILE.read_text())
    total = sum(d["done"] for d in data["daily"])
    print(f"\n📊 总进度: {total}题")
    print(f"📅 记录天数: {len(data['daily'])}天")
    
    # 显示最近7天
    print("\n最近7天:")
    for d in data["daily"][-7:]:
        bar = "█" * d["done"] + "░" * (5 - d["done"])
        print(f"  {d['date']}: [{bar}] {d['done']}题")

def generate_html():
    """生成带密码保护的HTML"""
    data = json.loads(DATA_FILE.read_text())
    plan = json.loads(PLAN_FILE.read_text())
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HDLBits Progress</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; 
               background: #0d1117; color: #c9d1d9; padding: 40px 20px; margin: 0; }}
        #login {{ text-align: center; margin-top: 100px; }}
        input {{ padding: 10px; font-size: 16px; border: 1px solid #30363d; 
                background: #21262d; color: white; border-radius: 6px; margin: 10px; }}
        button {{ padding: 10px 20px; background: #238636; color: white; border: none; 
                 border-radius: 6px; cursor: pointer; font-weight: 600; }}
        button:hover {{ background: #2ea043; }}
        .hidden {{ display: none; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #f0f6fc; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin: 24px 0; }}
        .stat-card {{ background: #161b22; border: 1px solid #30363d; padding: 16px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #58a6ff; }}
        .stat-label {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
        .heatmap {{ display: flex; gap: 3px; margin-top: 20px; overflow-x: auto; padding-bottom: 10px; }}
        .week {{ display: flex; flex-direction: column; gap: 3px; }}
        .day {{ width: 10px; height: 10px; border-radius: 2px; background: #161b22; border: 1px solid #21262d; }}
        .day.l1 {{ background: #0e4429; }}
        .day.l2 {{ background: #006d32; }}
        .day.l3 {{ background: #26a641; }}
        .day.l4 {{ background: #39d353; }}
        .day.missed {{ background: #f85149; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #30363d; }}
        th {{ color: #8b949e; font-weight: 500; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; 
                  background: #238636; color: white; }}
        .badge-warning {{ background: #f85149; }}
    </style>
</head>
<body>
    <div id="login">
        <h2>🔒 HDLBits Tracker</h2>
        <p>请输入访问密码</p>
        <input type="password" id="pwd" placeholder="password" onkeypress="if(event.key==='Enter')check()">
        <br>
        <button onclick="check()">进入</button>
        <p id="error" style="color: #f85149; display: none;">密码错误</p>
    </div>

    <div id="content" class="hidden">
        <div class="container">
            <h1>HDLBits 刷题进度</h1>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{sum(d["done"] for d in data["daily"])}</div>
                    <div class="stat-label">总题数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(data["daily"])}</div>
                    <div class="stat-label">天数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{(sum(d["done"] for d in data["daily"])/max(len(data["daily"]),1)):.1f}</div>
                    <div class="stat-label">日均</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{data["daily"][-1]["phase"] if data["daily"] else "未开始"}</div>
                    <div class="stat-label">当前阶段</div>
                </div>
            </div>

            <h3>刷题热力图</h3>
            <div id="heatmap" class="heatmap"></div>
            
            <h3>详细记录</h3>
            <table>
                <tr><th>日期</th><th>阶段</th><th>完成</th><th>题目</th><th>备注</th></tr>
                {''.join(f"<tr><td>{d['date']}</td><td>{d['phase']}</td><td>{d['done']}/{d['planned']}</td><td>{', '.join(d['problems'][:3])}{'...' if len(d['problems'])>3 else ''}</td><td>{d['note']}</td></tr>" for d in reversed(data["daily"][-20:]))}
            </table>
        </div>
    </div>

    <script>
        const PASSWORD = "hdl2026"; // 修改这里设置你的密码
        
        function check() {{
            if (document.getElementById('pwd').value === PASSWORD) {{
                document.getElementById('login').classList.add('hidden');
                document.getElementById('content').classList.remove('hidden');
                renderHeatmap();
            }} else {{
                document.getElementById('error').style.display = 'block';
            }}
        }}
        
        function renderHeatmap() {{
            const data = {json.dumps(data["daily"])};
            const container = document.getElementById('heatmap');
            const start = new Date("{plan["start_date"]}");
            
            for (let w = 0; w < 26; w++) {{
                const week = document.createElement('div');
                week.className = 'week';
                for (let d = 0; d < 7; d++) {{
                    const date = new Date(start);
                    date.setDate(start.getDate() + w * 7 + d);
                    const dateStr = date.toISOString().split('T')[0];
                    const entry = data.find(x => x.date === dateStr);
                    
                    const cell = document.createElement('div');
                    cell.className = 'day';
                    cell.title = dateStr;
                    
                    if (entry) {{
                        const level = Math.min(4, entry.done);
                        cell.className += ' l' + level;
                        if (entry.done < entry.planned) cell.className += ' missed';
                        cell.title += `: ${{entry.done}}题`;
                    }}
                    week.appendChild(cell);
                }}
                container.appendChild(week);
            }}
        }}
    </script>
</body>
</html>'''
    
    output = Path("docs/index.html")
    output.write_text(html, encoding='utf-8')
    print(f"✅ 已生成网站: {output.absolute()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="初始化")
    parser.add_argument("--add", type=int, metavar="N", help="记录N题")
    parser.add_argument("--problems", type=str, help="题目名，逗号分隔")
    parser.add_argument("--note", type=str, help="备注")
    parser.add_argument("--show", action="store_true", help="显示统计")
    parser.add_argument("--html", action="store_true", help="生成网站")
    
    args = parser.parse_args()
    
    if args.init:
        init()
    elif args.add is not None:
        add(args.add, args.problems.split(",") if args.problems else None, args.note)
    elif args.show:
        show()
    elif args.html:
        generate_html()
    else:
        show()

