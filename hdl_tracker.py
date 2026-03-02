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
    """生成带密码保护和计划显示的HTML"""
    data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    plan = json.loads(PLAN_FILE.read_text(encoding='utf-8'))
    
    # 确保docs目录存在
    Path("docs").mkdir(exist_ok=True)
    
    # 计算统计数据
    total_done = sum(d["done"] for d in data["daily"])
    unique_days = len(set(d["date"] for d in data["daily"]))
    avg = total_done / unique_days if unique_days > 0 else 0
    current_phase = data["daily"][-1]["phase"] if data["daily"] else plan["phases"][0]["name"]
    
    # 计算计划进度
    start = datetime.strptime(plan["start_date"], "%Y-%m-%d")
    today = datetime.now()
    days_passed = (today - start).days
    
    # 生成阶段进度HTML
    phase_html = ""
    cumulative_weeks = 0
    for p in plan["phases"]:
        # 计算该阶段的进度
        phase_done = sum(d["done"] for d in data["daily"] if d.get("phase") == p["name"])
        phase_pct = (phase_done / p["total"] * 100) if p["total"] > 0 else 0
        
        # 计算时间进度
        phase_start = start + timedelta(weeks=cumulative_weeks)
        phase_end = phase_start + timedelta(weeks=p["weeks"])
        phase_days = (today - phase_start).days
        time_pct = min(100, max(0, (phase_days / (p["weeks"] * 7)) * 100))
        
        # 判断是否当前阶段
        is_current = phase_start <= today < phase_end
        current_marker = " 🎯" if is_current else ""
        
        # 状态判断
        if phase_done >= p["total"]:
            status = "✅ 完成"
            status_color = "#3fb950"
        elif phase_pct >= time_pct:
            status = "🟢 正常"
            status_color = "#58a6ff"
        else:
            status = "🔴 落后"
            status_color = "#f85149"
        
        phase_html += f'''
        <div class="phase-item" style="margin-bottom: 16px; padding: 12px; background: #161b22; border-radius: 6px; border-left: 4px solid {p["color"]};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 600; color: #f0f6fc;">{p["name"]}{current_marker}</span>
                <span style="font-size: 12px; color: {status_color};">{status}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                <div style="flex: 1; height: 8px; background: #21262d; border-radius: 4px; overflow: hidden;">
                    <div style="width: {phase_pct}%; height: 100%; background: {p["color"]}; border-radius: 4px; transition: width 0.3s;"></div>
                </div>
                <span style="font-size: 12px; color: #8b949e; min-width: 60px; text-align: right;">{phase_done}/{p["total"]}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #8b949e;">
                <span>时间: {phase_start.strftime("%m/%d")} - {phase_end.strftime("%m/%d")}</span>
                <span>剩余: {max(0, p["total"] - phase_done)}题</span>
            </div>
        </div>
        '''
        
        cumulative_weeks += p["weeks"]
    
    # 整体计划统计
    total_plan = sum(p["total"] for p in plan["phases"])
    overall_pct = (total_done / total_plan * 100) if total_plan > 0 else 0
    days_left = (start + timedelta(weeks=cumulative_weeks) - today).days
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HDLBits Progress</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; 
               background: #0d1117; color: #c9d1d9; padding: 40px 20px; margin: 0; line-height: 1.5; }}
        #login {{ text-align: center; margin-top: 100px; }}
        input {{ padding: 10px; font-size: 16px; border: 1px solid #30363d; 
                background: #21262d; color: white; border-radius: 6px; margin: 10px; }}
        button {{ padding: 10px 20px; background: #238636; color: white; border: none; 
                 border-radius: 6px; cursor: pointer; font-weight: 600; }}
        button:hover {{ background: #2ea043; }}
        .hidden {{ display: none; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #f0f6fc; border-bottom: 1px solid #30363d; padding-bottom: 10px; margin-bottom: 24px; }}
        h2 {{ color: #f0f6fc; font-size: 18px; margin: 24px 0 12px 0; }}
        h3 {{ color: #8b949e; font-size: 14px; margin: 20px 0 10px 0; text-transform: uppercase; letter-spacing: 0.5px; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .stat-card {{ background: #161b22; border: 1px solid #30363d; padding: 16px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: 700; color: #58a6ff; margin-bottom: 4px; }}
        .stat-label {{ font-size: 12px; color: #8b949e; }}
        
        .plan-overview {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 24px; }}
        .plan-stats {{ display: flex; gap: 24px; margin-bottom: 16px; flex-wrap: wrap; }}
        .plan-stat {{ flex: 1; min-width: 120px; }}
        .plan-stat-value {{ font-size: 24px; font-weight: 600; color: #f0f6fc; }}
        .plan-stat-label {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
        
        .overall-progress {{ height: 12px; background: #21262d; border-radius: 6px; overflow: hidden; margin: 12px 0; }}
        .overall-bar {{ height: 100%; background: linear-gradient(90deg, #238636, #2ea043); border-radius: 6px; 
                       width: {overall_pct}%; transition: width 0.5s ease; }}
        
        .heatmap {{ display: flex; gap: 3px; margin-top: 16px; overflow-x: auto; padding-bottom: 10px; }}
        .week {{ display: flex; flex-direction: column; gap: 3px; }}
        .day {{ width: 10px; height: 10px; border-radius: 2px; background: #161b22; border: 1px solid #21262d; }}
        .day.l1 {{ background: #0e4429; }}
        .day.l2 {{ background: #006d32; }}
        .day.l3 {{ background: #26a641; }}
        .day.l4 {{ background: #39d353; }}
        .day.missed {{ background: #f85149; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }}
        th, td {{ padding: 10px 8px; text-align: left; border-bottom: 1px solid #30363d; }}
        th {{ color: #8b949e; font-weight: 500; font-size: 12px; text-transform: uppercase; }}
        
        .legend {{ display: flex; gap: 8px; align-items: center; margin-top: 16px; font-size: 12px; color: #8b949e; justify-content: flex-end; }}
        .legend-box {{ width: 10px; height: 10px; border-radius: 2px; }}
        
        @media (max-width: 600px) {{
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .plan-stats {{ flex-direction: column; gap: 12px; }}
        }}
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
            
            <!-- 统计卡片 -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{total_done}</div>
                    <div class="stat-label">总题数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{unique_days}</div>
                    <div class="stat-label">天数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{avg:.1f}</div>
                    <div class="stat-label">日均</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="font-size: 18px; padding-top: 6px;">{current_phase.replace("Phase ", "P")}</div>
                    <div class="stat-label">当前阶段</div>
                </div>
            </div>

            <!-- 计划概览 -->
            <div class="plan-overview">
                <h2>📅 18周计划概览</h2>
                <div class="plan-stats">
                    <div class="plan-stat">
                        <div class="plan-stat-value">{overall_pct:.1f}%</div>
                        <div class="plan-stat-label">总体完成度</div>
                    </div>
                    <div class="plan-stat">
                        <div class="plan-stat-value">{days_passed}</div>
                        <div class="plan-stat-label">已过天数</div>
                    </div>
                    <div class="plan-stat">
                        <div class="plan-stat-value" style="color: {('#3fb950' if days_left > 0 else '#f85149')}">{days_left}</div>
                        <div class="plan-stat-label">剩余天数</div>
                    </div>
                    <div class="plan-stat">
                        <div class="plan-stat-value">{total_done}/{total_plan}</div>
                        <div class="plan-stat-label">题目进度</div>
                    </div>
                </div>
                <div class="overall-progress">
                    <div class="overall-bar"></div>
                </div>
                
                <h3>各阶段详情</h3>
                {phase_html}
            </div>
            
            <!-- 热力图 -->
            <h2>🔥 刷题热力图</h2>
            <div id="heatmap" class="heatmap"></div>
            <div class="legend">
                <span>Less</span>
                <div class="legend-box" style="background: #161b22; border: 1px solid #21262d;"></div>
                <div class="legend-box" style="background: #0e4429;"></div>
                <div class="legend-box" style="background: #006d32;"></div>
                <div class="legend-box" style="background: #26a641;"></div>
                <div class="legend-box" style="background: #39d353;"></div>
                <span>More</span>
                <div style="width: 16px;"></div>
                <div class="legend-box" style="background: #f85149;"></div>
                <span>未达标</span>
            </div>
            
            <!-- 详细记录 -->
            <h2>📝 详细记录</h2>
            <table>
                <tr>
                    <th>日期</th>
                    <th>阶段</th>
                    <th>完成</th>
                    <th>题目</th>
                    <th>备注</th>
                </tr>
                {''.join(f"<tr><td>{d['date']}</td><td>{d['phase']}</td><td>{d['done']}/{d['planned']}</td><td>{', '.join(d['problems'][:3])}{'...' if len(d['problems'])>3 else ''}</td><td>{d['note'][:20]}{'...' if len(d['note'])>20 else ''}</td></tr>" for d in reversed(data["daily"][-30:]))}
            </table>
        </div>
    </div>

    <script>
        const PASSWORD = "hdl2026";
        
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
                        cell.title += `: ${{entry.done}}题 ${{entry.problems ? '('+entry.problems.join(',')+')' : ''}}`;
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

