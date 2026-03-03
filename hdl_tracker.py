#!/usr/bin/env python3
"""
HDLBits 进度追踪器 - 按章节记录
用法:
    python hdl_tracker.py --add 1 --problems "vector3" --chapter "Vectors"
    python hdl_tracker.py --add 1 --problems "mux2"     # 自动识别为Multiplexers
"""

import json
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(".hdlbits_tracker")
DATA_FILE = DATA_DIR / "data.json"
PLAN_FILE = DATA_DIR / "plan.json"

# 题目名到章节的映射（自动识别用）
PROBLEM_MAP = {
    # ========== Getting Started (2题) ==========
    "step_one": "Getting Started",
    "zero": "Getting Started",
    "output_zero": "Getting Started",
    
    # ========== Basics (17题) ==========
    "wire": "Basics",
    "wire4": "Basics",
    "notgate": "Basics",
    "andgate": "Basics",
    "norgate": "Basics",
    "xnorgate": "Basics",
    "wire_decl": "Basics",
    "7458": "Basics",
    "truthtable1": "Basics",
    "truthtable2": "Basics",
    "truthtable3": "Basics",
    "mt2015_eq2": "Basics",
    "mt2015_q4a": "Basics",
    "mt2015_q4b": "Basics",
    "mt2015_q4": "Basics",
    "ringer": "Basics",
    "thermostat": "Basics",
    "popcount3": "Basics",
    "gatesv": "Basics",
    "gatesv100": "Basics",
    
    # ========== Vectors (9题) ==========
    "vector0": "Vectors",
    "vector1": "Vectors",
    "vector2": "Vectors",
    "vector3": "Vectors",
    "vectorr": "Vectors",
    "vector4": "Vectors",
    "vector5": "Vectors",
    "vector6": "Vectors",
    "vector7": "Vectors",
    "vector100": "Vectors",
    "vector100r": "Vectors",
    "vectorgates": "Vectors",
    "gates4": "Vectors",
    "vector9": "Vectors",
    "vector10": "Vectors",
    
    # ========== Modules: Hierarchy (9题) ==========
    "module": "Modules: Hierarchy",
    "module_pos": "Modules: Hierarchy",
    "module_name": "Modules: Hierarchy",
    "module_shift": "Modules: Hierarchy",
    "module_shift8": "Modules: Hierarchy",
    "module_add": "Modules: Hierarchy",
    "module_fadd": "Modules: Hierarchy",
    "module_cseladd": "Modules: Hierarchy",
    "module_addsub": "Modules: Hierarchy",
    "module_addsubb": "Modules: Hierarchy",
    
    # ========== Procedures (8题) ==========
    "alwaysblock1": "Procedures",
    "alwaysblock2": "Procedures",
    "assign_vs_always": "Procedures",
    "blocking_nonblocking": "Procedures",
    "if_statement": "Procedures",
    "if_statement_latches": "Procedures",
    "case_statement": "Procedures",
    "priority_encoder": "Procedures",
    "priority_encoder_with_casez": "Procedures",
    "avoiding_latches": "Procedures",
    
    # ========== More Verilog Features (7题) ==========
    "conditional": "More Verilog Features",
    "reduction": "More Verilog Features",
    "gates100": "More Verilog Features",
    "vector100r": "More Verilog Features",
    "popcount255": "More Verilog Features",
    "adder100i": "More Verilog Features",
    "bcdadd100": "More Verilog Features",
    
    # ========== Basic Gates (17题) ==========
    "wire_circ": "Basic Gates",
    "gnd": "Basic Gates",
    "nor_circ": "Basic Gates",
    "another_gate": "Basic Gates",
    "two_gates": "Basic Gates",
    "more_logic_gates": "Basic Gates",
    "7420_circ": "Basic Gates",
    "truthtable1_circ": "Basic Gates",
    "truthtable2_circ": "Basic Gates",
    "truthtable3_circ": "Basic Gates",
    "mt2015_eq2_circ": "Basic Gates",
    "mt2015_q4a_circ": "Basic Gates",
    "mt2015_q4b_circ": "Basic Gates",
    "mt2015_q4_circ": "Basic Gates",
    "ringer_circ": "Basic Gates",
    "thermostat_circ": "Basic Gates",
    "popcount3_circ": "Basic Gates",
    
    # ========== Multiplexers (12题) ==========
    "mux2to1": "Multiplexers",
    "mux2to1v": "Multiplexers",
    "mux9to1v": "Multiplexers",
    "mux256to1": "Multiplexers",
    "mux256to1v": "Multiplexers",
    "hadd": "Multiplexers",
    "fadd": "Multiplexers",
    "add3": "Multiplexers",
    "muxadd": "Multiplexers",
    "adder": "Multiplexers",
    "signed_addition_overflow": "Multiplexers",
    "bcd_adder": "Multiplexers",
    
    # ========== Arithmetic Circuits (7题) ==========
    "carry_select_adder": "Arithmetic Circuits",
    "addsub_100bit": "Arithmetic Circuits",
    "adder_100bit": "Arithmetic Circuits",
    "signed_addition": "Arithmetic Circuits",
    "overflow": "Arithmetic Circuits",
    "100bit_binary_adder": "Arithmetic Circuits",
    "4digit_bcd_adder": "Arithmetic Circuits",
    
    # ========== Karnaugh Map to Circuit (8题) ==========
    "kmap1": "Karnaugh Map to Circuit",
    "kmap2": "Karnaugh Map to Circuit",
    "kmap3": "Karnaugh Map to Circuit",
    "kmap4": "Karnaugh Map to Circuit",
    "exams_ece241_2014_q3": "Karnaugh Map to Circuit",
    "exams_m2014_q3": "Karnaugh Map to Circuit",
    "exams_2012_q1g": "Karnaugh Map to Circuit",
    "exams_2012_q1h": "Karnaugh Map to Circuit",
    
    # ========== Latches and Flip-Flops (18题) ==========
    "dff": "Latches and Flip-Flops",
    "dff8": "Latches and Flip-Flops",
    "dff8r": "Latches and Flip-Flops",
    "dff8p": "Latches and Flip-Flops",
    "dff8ar": "Latches and Flip-Flops",
    "dff16e": "Latches and Flip-Flops",
    "muxdff": "Latches and Flip-Flops",
    "detect_edge": "Latches and Flip-Flops",
    "dual_edge": "Latches and Flip-Flops",
    "edge_capture": "Latches and Flip-Flops",
    "dff_sr": "Latches and Flip-Flops",
    "dff_jk": "Latches and Flip-Flops",
    "dff_t": "Latches and Flip-Flops",
    "latch": "Latches and Flip-Flops",
    "latch_if": "Latches and Flip-Flops",
    "latch_always": "Latches and Flip-Flops",
    "exams_ece241_2014_q4a": "Latches and Flip-Flops",
    "exams_ece241_2014_q4b": "Latches and Flip-Flops",
    
    # ========== Counters (8题) ==========
    "count15": "Counters",
    "count10": "Counters",
    "count1to10": "Counters",
    "countslow": "Counters",
    "counter_1_12": "Counters",
    "counter_1000": "Counters",
    "4digit_decimal_counter": "Counters",
    "12hour_clock": "Counters",
    "exams_ece241_2014_q7a": "Counters",
    "exams_ece241_2014_q7b": "Counters",
    "countbcd": "Counters",
    "count_ones": "Counters",
    
    # ========== Shift Registers (9题) ==========
    "shift4": "Shift Registers",
    "rotate100": "Shift Registers",
    "shift18": "Shift Registers",
    "lfsr5": "Shift Registers",
    "lfsr3": "Shift Registers",
    "lfsr32": "Shift Registers",
    "shift_register": "Shift Registers",
    "shift_register2": "Shift Registers",
    "3input_lut": "Shift Registers",
    "m2014_q4k": "Shift Registers",
    "exams_2014_q4": "Shift Registers",
    "exams_ece241_2014_q5a": "Shift Registers",
    "exams_ece241_2014_q5b": "Shift Registers",
    
    # ========== More Circuits (3题) ==========
    "rule90": "More Circuits",
    "rule110": "More Circuits",
    "conwaylife": "More Circuits",
    "conways_game_of_life": "More Circuits",
    "exams_ece241_2014_q6a": "More Circuits",
    "exams_ece241_2014_q6b": "More Circuits",
    "exams_ece241_2014_q6c": "More Circuits",
    "exams_2012_q2a": "More Circuits",
    "exams_2012_q2b": "More Circuits",
    "exams_2012_q2c": "More Circuits",
    "exams_2012_q2d": "More Circuits",
    
    # ========== Simple FSM (8题) ==========
    "fsm1": "Simple FSM",
    "fsm1s": "Simple FSM",
    "fsm2": "Simple FSM",
    "fsm2s": "Simple FSM",
    "fsm3comb": "Simple FSM",
    "fsm3onehot": "Simple FSM",
    "fsm3": "Simple FSM",
    "fsm3s": "Simple FSM",
    "design_a_moore_fsm": "Simple FSM",
    
    # ========== Complex FSM (22题) ==========
    "exams_2014_q3fsm": "Complex FSM",
    "exams_ece241_2014_q4": "Complex FSM",
    "lemmings1": "Complex FSM",
    "lemmings2": "Complex FSM",
    "lemmings3": "Complex FSM",
    "lemmings4": "Complex FSM",
    "onehot_fsm": "Complex FSM",
    "ps2_packet_parser": "Complex FSM",
    "ps2_packet_parser_and_datapath": "Complex FSM",
    "serial_receiver": "Complex FSM",
    "serial_receiver_and_datapath": "Complex FSM",
    "serial_receiver_with_parity_checking": "Complex FSM",
    "sequence_recognition": "Complex FSM",
    "q8_design_a_mealy_fsm": "Complex FSM",
    "q5a_serial_twos_complementer_moore": "Complex FSM",
    "q5b_serial_twos_complementer_mealy": "Complex FSM",
    "q3a_fsm": "Complex FSM",
    "q3b_fsm": "Complex FSM",
    "q3c_fsm_logic": "Complex FSM",
    "q6b_fsm_next_state_logic": "Complex FSM",
    "q6c_fsm_one_hot_next_state_logic": "Complex FSM",
    "exams_ece241_2013_q4": "Complex FSM",
    "exams_ece241_2013_q5": "Complex FSM",
    "exams_2012_q5a": "Complex FSM",
    "exams_2012_q5b": "Complex FSM",
    "exams_2012_q5c": "Complex FSM",
    "exams_2012_q5d": "Complex FSM",
    
    # ========== Building Larger Circuits (7题) ==========
    "count_clock": "Building Larger Circuits",
    "counter_with_period_1000": "Building Larger Circuits",
    "4bit_shift_register_and_down_counter": "Building Larger Circuits",
    "fsm_sequence_1101_recognizer": "Building Larger Circuits",
    "fsm_enable_shift_register": "Building Larger Circuits",
    "fsm_the_complete_fsm": "Building Larger Circuits",
    "the_complete_timer": "Building Larger Circuits",
    "fsm_one_hot_logic_equations": "Building Larger Circuits",
    "exams_ece241_2014_q2": "Building Larger Circuits",
    "exams_ece241_2013_q2": "Building Larger Circuits",
    "exams_2012_q4a": "Building Larger Circuits",
    "exams_2012_q4b": "Building Larger Circuits",
    "exams_2012_q4c": "Building Larger Circuits",
    "exams_2012_q4d": "Building Larger Circuits",
    
    # ========== Reading Simulations (15题) ==========
    "simulation1": "Reading Simulations",
    "simulation2": "Reading Simulations",
    "simulation3": "Reading Simulations",
    "simulation4": "Reading Simulations",
    "simulation5": "Reading Simulations",
    "simulation6": "Reading Simulations",
    "simulation7": "Reading Simulations",
    "simulation8": "Reading Simulations",
    "simulation9": "Reading Simulations",
    "simulation10": "Reading Simulations",
    "simulation11": "Reading Simulations",
    "simulation12": "Reading Simulations",
    "simulation13": "Reading Simulations",
    "simulation14": "Reading Simulations",
    "simulation15": "Reading Simulations",
    
    # ========== Finding bugs in code (5题) ==========
    "bugs1": "Finding bugs in code",
    "bugs2": "Finding bugs in code",
    "bugs3": "Finding bugs in code",
    "bugs4": "Finding bugs in code",
    "bugs5": "Finding bugs in code",
    "mux_bug": "Finding bugs in code",
    "nand_bug": "Finding bugs in code",
    "add_sub_bug": "Finding bugs in code",
    "case_statement_bug": "Finding bugs in code",
    
    # ========== Build from waveform (10题) ==========
    "waveform1": "Build from waveform",
    "waveform2": "Build from waveform",
    "waveform3": "Build from waveform",
    "waveform4": "Build from waveform",
    "waveform5": "Build from waveform",
    "waveform6": "Build from waveform",
    "waveform7": "Build from waveform",
    "waveform8": "Build from waveform",
    "waveform9": "Build from waveform",
    "waveform10": "Build from waveform",
    "combinational_circuit_1": "Build from waveform",
    "combinational_circuit_2": "Build from waveform",
    "combinational_circuit_3": "Build from waveform",
    "combinational_circuit_4": "Build from waveform",
    "combinational_circuit_5": "Build from waveform",
    "combinational_circuit_6": "Build from waveform",
    "sequential_circuit_7": "Build from waveform",
    "sequential_circuit_8": "Build from waveform",
    "sequential_circuit_9": "Build from waveform",
    "sequential_circuit_10": "Build from waveform",
    
    # ========== Writing Testbenches (5题) ==========
    "tb1": "Writing Testbenches",
    "tb2": "Writing Testbenches",
    "tb3": "Writing Testbenches",
    "tb4": "Writing Testbenches",
    "tb5": "Writing Testbenches",
    "clock": "Writing Testbenches",
    "testbench1": "Writing Testbenches",
    "testbench2": "Writing Testbenches",
    "and_gate_tb": "Writing Testbenches",
    "t_flip_flop_tb": "Writing Testbenches",
}

DEFAULT_PLAN = {
    "start_date": datetime.now().strftime("%Y-%m-%d"),
    "daily_goal": 2,
    "phases": [
        {
            "name": "Getting Started",
            "category": "入门",
            "weeks": 0.5,
            "chapters": [{"name": "Getting Started", "problems": 2}]
        },
        {
            "name": "Verilog Language",
            "category": "语法基础", 
            "weeks": 2.5,
            "chapters": [
                {"name": "Basics", "problems": 12},
                {"name": "Vectors", "problems": 11},
                {"name": "Modules: Hierarchy", "problems": 10},
                {"name": "Procedures", "problems": 8},
                {"name": "More Verilog Features", "problems": 8}
            ]
        },
        {
            "name": "Combinational Logic",
            "category": "组合逻辑",
            "weeks": 4,
            "chapters": [
                {"name": "Basic Gates", "problems": 15},
                {"name": "Multiplexers", "problems": 12},
                {"name": "Arithmetic Circuits", "problems": 12},
                {"name": "Karnaugh Map to Circuit", "problems": 8}
            ]
        },
        {
            "name": "Sequential Logic",
            "category": "时序逻辑",
            "weeks": 4,
            "chapters": [
                {"name": "Latches and Flip-Flops", "problems": 18},
                {"name": "Counters", "problems": 8},
                {"name": "Shift Registers", "problems": 9},
                {"name": "More Circuits", "problems": 10}
            ]
        },
        {
            "name": "Finite State Machines",
            "category": "状态机",
            "weeks": 4,
            "chapters": [
                {"name": "Simple FSM", "problems": 8},
                {"name": "Complex FSM", "problems": 12},
                {"name": "Building Larger Circuits", "problems": 7}
            ]
        },
        {
            "name": "Verification",
            "category": "验证",
            "weeks": 3,
            "chapters": [
                {"name": "Reading Simulations", "problems": 15},
                {"name": "Finding bugs in code", "problems": 10},
                {"name": "Build from waveform", "problems": 5},
                {"name": "Writing Testbenches", "problems": 8}
            ]
        }
    ]
}

def init():
    DATA_DIR.mkdir(exist_ok=True)
    if not PLAN_FILE.exists():
        with open(PLAN_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PLAN, f, indent=2, ensure_ascii=False)
    if not DATA_FILE.exists():
        data = {"start_date": DEFAULT_PLAN["start_date"], "daily": []}
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ 初始化完成")

def get_chapter_from_problem(problem_name):
    """根据题目名自动识别章节"""
    return PROBLEM_MAP.get(problem_name.lower(), "Unknown")

def get_phase_from_chapter(chapter_name, plan):
    """根据章节查找所属阶段"""
    for phase in plan["phases"]:
        for ch in phase["chapters"]:
            if ch["name"] == chapter_name:
                return phase["name"]
    return "Unknown"

def add(count, problems=None, note=None, chapter=None):
    """记录进度（自动识别章节）"""
    data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    plan = json.loads(PLAN_FILE.read_text(encoding='utf-8'))
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 自动识别章节
    auto_chapters = set()
    if problems:
        for p in problems:
            ch = get_chapter_from_problem(p)
            if ch != "Unknown":
                auto_chapters.add(ch)
    
    # 使用指定章节或自动识别的第一个
    target_chapter = chapter or (list(auto_chapters)[0] if auto_chapters else "Unknown")
    target_phase = get_phase_from_chapter(target_chapter, plan)
    
    # 检查是否已有今日记录
    existing_idx = None
    for i, d in enumerate(data["daily"]):
        if d["date"] == today:
            existing_idx = i
            break
    
    if existing_idx is not None:
        old = data["daily"][existing_idx]
        old["done"] += count
        if problems:
            old["problems"].extend(problems)
        if target_chapter != "Unknown" and target_chapter not in old.get("chapters", []):
            old.setdefault("chapters", []).append(target_chapter)
        if note:
            old["note"] = (old["note"] + "; " + note) if old["note"] else note
        
        status = "✅" if old["done"] >= old["planned"] else "⚠️"
        print(f"{status} 追加: {today} - 累计{old['done']}题 ({target_chapter})")
    else:
        entry = {
            "date": today,
            "done": count,
            "planned": plan["daily_goal"],
            "phase": target_phase,
            "chapters": [target_chapter] if target_chapter != "Unknown" else [],
            "problems": problems or [],
            "note": note or ""
        }
        data["daily"].append(entry)
        status = "✅" if count >= plan["daily_goal"] else "⚠️"
        print(f"{status} 记录: {today} - {count}题 ({target_chapter})")
    
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def show():
    """显示章节进度"""
    data = json.loads(DATA_FILE.read_text())
    plan = json.loads(PLAN_FILE.read_text())
    
    print(f"\n📊 总进度: {sum(d['done'] for d in data['daily'])}题")
    
    # 按章节统计
    chapter_stats = {}
    for d in data["daily"]:
        for ch in d.get("chapters", []):
            chapter_stats[ch] = chapter_stats.get(ch, 0) + d["done"]
    
    print("\n各章节进度:")
    for phase in plan["phases"]:
        print(f"\n【{phase['category']}】- {phase['name']}")
        for ch in phase["chapters"]:
            done = chapter_stats.get(ch["name"], 0)
            pct = done / ch["problems"] * 100
            bar = "█" * int(pct/10) + "░" * (10 - int(pct/10))
            print(f"  {ch['name'][:20]:20} [{bar}] {done}/{ch['problems']} ({pct:.0f}%)")

def generate_html():
    """生成按章节分类的网站"""
    data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    plan = json.loads(PLAN_FILE.read_text(encoding='utf-8'))
    
    Path("docs").mkdir(exist_ok=True)
    
    # 统计数据
    total_done = sum(d["done"] for d in data["daily"])
    unique_days = len(set(d["date"] for d in data["daily"]))
    avg = total_done / unique_days if unique_days > 0 else 0
    
    # 计算各章节完成度
    chapter_done = {}
    for d in data["daily"]:
        for ch in d.get("chapters", []):
            chapter_done[ch] = chapter_done.get(ch, 0) + d["done"]
    
    # 生成章节进度HTML
    chapters_html = ""
    for phase in plan["phases"]:
        phase_total_done = sum(chapter_done.get(ch["name"], 0) for ch in phase["chapters"])
        phase_total_plan = sum(ch["problems"] for ch in phase["chapters"])
        phase_pct = phase_total_done / phase_total_plan * 100 if phase_total_plan > 0 else 0
        
        chapters_html += f'''
        <div class="phase-section" style="margin-bottom: 24px; background: #161b22; border-radius: 8px; padding: 16px; border-left: 4px solid #58a6ff;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; color: #f0f6fc;">{phase["category"]} · {phase["name"]}</h3>
                <span style="font-size: 14px; color: #8b949e;">{phase_total_done}/{phase_total_plan} ({phase_pct:.0f}%)</span>
            </div>
            <div style="height: 8px; background: #21262d; border-radius: 4px; margin-bottom: 12px;">
                <div style="height: 100%; width: {phase_pct}%; background: linear-gradient(90deg, #238636, #2ea043); border-radius: 4px;"></div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px;">
        '''
        
        for ch in phase["chapters"]:
            done = chapter_done.get(ch["name"], 0)
            pct = done / ch["problems"] * 100
            status = "✅" if done >= ch["problems"] else ("🟢" if pct > 50 else "⚪")
            
            chapters_html += f'''
                <div style="background: #0d1117; padding: 10px; border-radius: 6px; font-size: 13px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span>{ch["name"]}</span>
                        <span>{status} {done}/{ch["problems"]}</span>
                    </div>
                    <div style="height: 4px; background: #21262d; border-radius: 2px;">
                        <div style="height: 100%; width: {pct}%; background: #58a6ff; border-radius: 2px;"></div>
                    </div>
                </div>
            '''
        
        chapters_html += '</div></div>'
    
    # 生成HTML（简化版，完整版类似之前）
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HDLBits Tracker - By Chapter</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; 
               background: #0d1117; color: #c9d1d9; padding: 40px 20px; margin: 0; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #f0f6fc; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 20px 0; }}
        .stat-card {{ background: #161b22; border: 1px solid #30363d; padding: 16px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #58a6ff; }}
        #login {{ text-align: center; margin-top: 100px; }}
        input {{ padding: 10px; font-size: 16px; border: 1px solid #30363d; 
                background: #21262d; color: white; border-radius: 6px; margin: 10px; }}
        button {{ padding: 10px 20px; background: #238636; color: white; border: none; 
                 border-radius: 6px; cursor: pointer; font-weight: 600; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div id="login">
        <h2>🔒 HDLBits Tracker</h2>
        <input type="password" id="pwd" placeholder="password" onkeypress="if(event.key==='Enter')check()">
        <br><button onclick="check()">进入</button>
        <p id="error" style="color: #f85149; display: none;">密码错误</p>
    </div>
    
    <div id="content" class="hidden container">
        <h1>HDLBits 刷题进度</h1>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total_done}</div>
                <div style="font-size: 12px; color: #8b949e;">总题数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{unique_days}</div>
                <div style="font-size: 12px; color: #8b949e;">天数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg:.1f}</div>
                <div style="font-size: 12px; color: #8b949e;">日均</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="font-size: 16px;">{len([c for c in chapter_done.values() if c > 0])}</div>
                <div style="font-size: 12px; color: #8b949e;">已开始章节</div>
            </div>
        </div>
        
        <h2>📚 章节进度</h2>
        {chapters_html}
        
        <h2>📝 最近记录</h2>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <tr style="border-bottom: 1px solid #30363d;">
                <th style="text-align: left; padding: 8px; color: #8b949e;">日期</th>
                <th style="text-align: left; padding: 8px; color: #8b949e;">章节</th>
                <th style="text-align: left; padding: 8px; color: #8b949e;">题目</th>
            </tr>
            {''.join(f"<tr style='border-bottom: 1px solid #21262d;'><td style='padding: 8px;'>{d['date']}</td><td style='padding: 8px;'>{', '.join(d.get('chapters', []))}</td><td style='padding: 8px;'>{', '.join(d['problems'])}</td></tr>" for d in reversed(data["daily"][-10:]))}
        </table>
    </div>
    
    <script>
        function check() {{
            if (document.getElementById('pwd').value === 'hdl2026') {{
                document.getElementById('login').classList.add('hidden');
                document.getElementById('content').classList.remove('hidden');
            }} else {{
                document.getElementById('error').style.display = 'block';
            }}
        }}
    </script>
</body>
</html>'''
    
    Path("docs/index.html").write_text(html, encoding='utf-8')
    print("✅ 已生成章节版网站")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--add", type=int, metavar="N")
    parser.add_argument("--problems", type=str)
    parser.add_argument("--chapter", type=str, help="指定章节（如 Vectors）")
    parser.add_argument("--note", type=str)
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--html", action="store_true")
    
    args = parser.parse_args()
    
    if args.init:
        init()
    elif args.add is not None:
        problems = args.problems.split(",") if args.problems else None
        add(args.add, problems, args.note, args.chapter)
    elif args.show:
        show()
    elif args.html:
        generate_html()
    else:
        show()