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
    
    # ========== Basics (8题) ==========
    "wire": "Basics",
    "wire4": "Basics",
    "notgate": "Basics",
    "andgate": "Basics",
    "norgate": "Basics",
    "xnorgate": "Basics",
    "wire_decl": "Basics",
    "7458": "Basics",
    
    # ========== Vectors (9题) ==========
    "vector0": "Vectors",
    "vector1": "Vectors",
    "vector2": "Vectors",
    "vectorgates": "Vectors",
    "gates4": "Vectors",
    "vector3": "Vectors",
    "vectorr": "Vectors",
    "vector4": "Vectors",
    "vector5": "Vectors",
    
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
    
    # ========== Procedures (8题) ==========
    "alwaysblock1": "Procedures",
    "alwaysblock2": "Procedures",
    "always_if": "Procedures",
    "always_if2": "Procedures",
    "always_case": "Procedures",
    "always_case2": "Procedures",
    "always_casez": "Procedures",
    "always_nolatches": "Procedures",
    
    # ========== More Verilog Features (7题) ==========
    "conditional": "More Verilog Features",
    "reduction": "More Verilog Features",
    "gates100": "More Verilog Features",
    "vector100r": "More Verilog Features",
    "popcount255": "More Verilog Features",
    "adder100i": "More Verilog Features",
    "bcdadd100": "More Verilog Features",
    
    # ========== Basic Gates (17题) ==========
    "exams/m2014_q4h": "Basic Gates",
    "exams/m2014_q4i": "Basic Gates",
    "exams/m2014_q4e": "Basic Gates",
    "exams/m2014_q4f": "Basic Gates",
    "exams/m2014_q4g": "Basic Gates",
    "gates": "Basic Gates",
    "7420": "Basic Gates",
    "truthtable1": "Basic Gates",
    "mt2015_eq2": "Basic Gates",
    "mt2015_q4a": "Basic Gates",
    "mt2015_q4b": "Basic Gates",
    "mt2015_q4": "Basic Gates",
    "ringer": "Basic Gates",
    "thermostat": "Basic Gates",
    "popcount3": "Basic Gates",
    "gatesv": "Basic Gates",
    "gatesv100": "Basic Gates",
    
    # ========== Multiplexers (5题) ==========
    "mux2to1": "Multiplexers",
    "mux2to1v": "Multiplexers",
    "mux9to1v": "Multiplexers",
    "mux256to1": "Multiplexers",
    "mux256to1v": "Multiplexers",
    
    # ========== Arithmetic Circuits (7题) ==========
    "hadd": "Arithmetic Circuits",
    "fadd": "Arithmetic Circuits",
    "adder3": "Arithmetic Circuits",
    "exams/m2014_q4j": "Arithmetic Circuits",
    "exams/ece241_2014_q1c": "Arithmetic Circuits",
    "adder100": "Arithmetic Circuits",
    "bcdadd4": "Arithmetic Circuits",
    
    # ========== Karnaugh Map to Circuit (8题) ==========
    "kmap1": "Karnaugh Map to Circuit",
    "kmap2": "Karnaugh Map to Circuit",
    "kmap3": "Karnaugh Map to Circuit",
    "kmap4": "Karnaugh Map to Circuit",
    "exams/ece241_2013_q2": "Karnaugh Map to Circuit",
    "exams/m2014_q3": "Karnaugh Map to Circuit",
    "exams/2012_q1g": "Karnaugh Map to Circuit",
    "exams/ece241_2014_q3": "Karnaugh Map to Circuit",
    
    # ========== Latches and Flip-Flops (18题) ==========
    "dff": "Latches and Flip-Flops",
    "dff8": "Latches and Flip-Flops",
    "dff8r": "Latches and Flip-Flops",
    "dff8p": "Latches and Flip-Flops",
    "dff8ar": "Latches and Flip-Flops",
    "dff16e": "Latches and Flip-Flops",
    "exams/m2014_q4a": "Latches and Flip-Flops",
    "exams/m2014_q4b": "Latches and Flip-Flops",
    "exams/m2014_q4c": "Latches and Flip-Flops",
    "exams/m2014_q4d": "Latches and Flip-Flops",
    "mt2015_muxdff": "Latches and Flip-Flops",
    "exams/2014_q4a": "Latches and Flip-Flops",
    "exams/ece241_2014_q4": "Latches and Flip-Flops",
    "exams/ece241_2013_q7": "Latches and Flip-Flops",
    "edgedetect": "Latches and Flip-Flops",
    "edgedetect2": "Latches and Flip-Flops",
    "edgecapture": "Latches and Flip-Flops",
    "dualedge": "Latches and Flip-Flops",
    
    # ========== Counters (8题) ==========
    "count15": "Counters",
    "count10": "Counters",
    "count1to10": "Counters",
    "countslow": "Counters",
    "exams/ece241_2014_q7a": "Counters",
    "exams/ece241_2014_q7b": "Counters",
    "countbcd": "Counters",
    "count_clock": "Counters",
    
    # ========== Shift Registers (9题) ==========
    "shift4": "Shift Registers",
    "rotate100": "Shift Registers",
    "shift18": "Shift Registers",
    "lfsr5": "Shift Registers",
    "mt2015_lfsr": "Shift Registers",
    "lfsr32": "Shift Registers",
    "exams/m2014_q4k": "Shift Registers",
    "exams/2014_q4b": "Shift Registers",
    "exams/ece241_2013_q12": "Shift Registers",
    
    # ========== More Circuits (3题) ==========
    "rule90": "More Circuits",
    "rule110": "More Circuits",
    "conwaylife": "More Circuits",
    
    # ========== Finite State Machines (33题) ==========
    "fsm1": "Finite State Machines",
    "fsm1s": "Finite State Machines",
    "fsm2": "Finite State Machines",
    "fsm2s": "Finite State Machines",
    "fsm3comb": "Finite State Machines",
    "fsm3onehot": "Finite State Machines",
    "fsm3": "Finite State Machines",
    "fsm3s": "Finite State Machines",
    "exams/ece241_2013_q4": "Finite State Machines",
    "lemmings1": "Finite State Machines",
    "lemmings2": "Finite State Machines",
    "lemmings3": "Finite State Machines",
    "lemmings4": "Finite State Machines",
    "fsm_onehot": "Finite State Machines",
    "fsm_ps2": "Finite State Machines",
    "fsm_ps2data": "Finite State Machines",
    "fsm_serial": "Finite State Machines",
    "fsm_serialdata": "Finite State Machines",
    "fsm_serialdp": "Finite State Machines",
    "fsm_hdlc": "Finite State Machines",
    "exams/ece241_2013_q8": "Finite State Machines",
    "exams/ece241_2014_q5a": "Finite State Machines",
    "exams/ece241_2014_q5b": "Finite State Machines",
    "exams/2014_q3fsm": "Finite State Machines",
    "exams/2014_q3bfsm": "Finite State Machines",
    "exams/2014_q3c": "Finite State Machines",
    "exams/m2014_q6b": "Finite State Machines",
    "exams/m2014_q6c": "Finite State Machines",
    "exams/m2014_q6": "Finite State Machines",
    "exams/2012_q2fsm": "Finite State Machines",
    "exams/2012_q2b": "Finite State Machines",
    "exams/2013_q2afsm": "Finite State Machines",
    "exams/2013_q2bfsm": "Finite State Machines",
    
    # ========== Building Larger Circuits (7题) ==========
    "exams/review2015_count1k": "Building Larger Circuits",
    "exams/review2015_shiftcount": "Building Larger Circuits",
    "exams/review2015_fsmseq": "Building Larger Circuits",
    "exams/review2015_fsmshift": "Building Larger Circuits",
    "exams/review2015_fsm": "Building Larger Circuits",
    "exams/review2015_fancytimer": "Building Larger Circuits",
    "exams/review2015_fsmonehot": "Building Larger Circuits",
    
    # ========== Finding bugs in code (5题) ==========
    "bugs_mux2": "Finding bugs in code",
    "bugs_nand3": "Finding bugs in code",
    "bugs_mux4": "Finding bugs in code",
    "bugs_addsubz": "Finding bugs in code",
    "bugs_case": "Finding bugs in code",
    
    # ========== Build from waveform (10题) ==========
    "sim/circuit1": "Build from waveform",
    "sim/circuit2": "Build from waveform",
    "sim/circuit3": "Build from waveform",
    "sim/circuit4": "Build from waveform",
    "sim/circuit5": "Build from waveform",
    "sim/circuit6": "Build from waveform",
    "sim/circuit7": "Build from waveform",
    "sim/circuit8": "Build from waveform",
    "sim/circuit9": "Build from waveform",
    "sim/circuit10": "Build from waveform",
    
    # ========== Writing Testbenches (5题) ==========
    "tb/clock": "Writing Testbenches",
    "tb/tb1": "Writing Testbenches",
    "tb/and": "Writing Testbenches",
    "tb/tb2": "Writing Testbenches",
    "tb/tff": "Writing Testbenches",
    
    # ========== CS450 (4题) ==========
    "cs450/timer": "CS450",
    "cs450/counter_2bc": "CS450",
    "cs450/history_shift": "CS450",
    "cs450/gshare": "CS450",
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
    """根据题目名自动识别章节（不区分大小写，支持部分匹配）"""
    # 统一转小写，并去掉可能的路径前缀
    clean_name = problem_name.lower().strip()
    # 如果包含斜杠，只取最后部分（如 exams/m2014_q4h -> m2014_q4h）
    if '/' in clean_name:
        clean_name = clean_name.split('/')[-1]
    
    # 直接匹配
    if clean_name in PROBLEM_MAP:
        return PROBLEM_MAP[clean_name]
    
    # 模糊匹配（如 module_pos 匹配到 module_pos）
    for key, chapter in PROBLEM_MAP.items():
        # 去掉key的路径前缀再比较
        key_clean = key.split('/')[-1] if '/' in key else key
        if key_clean == clean_name:
            return chapter
    
    return "Unknown"

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
    """生成网站（修复章节统计逻辑）"""
    import json
    from pathlib import Path
    from datetime import datetime, timedelta
    
    DATA_FILE = Path(".hdlbits_tracker/data.json")
    PLAN_FILE = Path(".hdlbits_tracker/plan.json")
    
    data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    plan = json.loads(PLAN_FILE.read_text(encoding='utf-8'))
    
    Path("docs").mkdir(exist_ok=True)
    
    # ========== 修复1：按题目统计章节进度（不再按天累加） ==========
    def get_chapter_from_problem(problem_name):
        """根据题目名识别章节（不区分大小写）"""
        if not problem_name:
            return "Unknown"
        
        # 清理题目名（转小写，去空格）
        clean = problem_name.lower().strip()
        if '/' in clean:
            clean = clean.split('/')[-1]
        
        # 完整映射表（包含所有175题）
        PROBLEM_MAP = {
            # Getting Started (2)
            "step_one": "Getting Started",
            "zero": "Getting Started",
            
            # Basics (8)
            "wire": "Basics", "wire4": "Basics", "notgate": "Basics", 
            "andgate": "Basics", "norgate": "Basics", "xnorgate": "Basics",
            "wire_decl": "Basics", "7458": "Basics",
            
            # Vectors (9)
            "vector0": "Vectors", "vector1": "Vectors", "vector2": "Vectors",
            "vectorgates": "Vectors", "gates4": "Vectors", "vector3": "Vectors",
            "vectorr": "Vectors", "vector4": "Vectors", "vector5": "Vectors",
            
            # Modules: Hierarchy (9)
            "module": "Modules: Hierarchy", "module_pos": "Modules: Hierarchy",
            "module_name": "Modules: Hierarchy", "module_shift": "Modules: Hierarchy",
            "module_shift8": "Modules: Hierarchy", "module_add": "Modules: Hierarchy",
            "module_fadd": "Modules: Hierarchy", "module_cseladd": "Modules: Hierarchy",
            "module_addsub": "Modules: Hierarchy",
            
            # Procedures (8)
            "alwaysblock1": "Procedures", "alwaysblock2": "Procedures",
            "always_if": "Procedures", "always_if2": "Procedures",
            "always_case": "Procedures", "always_case2": "Procedures",
            "always_casez": "Procedures", "always_nolatches": "Procedures",
            
            # More Verilog Features (7)
            "conditional": "More Verilog Features", "reduction": "More Verilog Features",
            "gates100": "More Verilog Features", "vector100r": "More Verilog Features",
            "popcount255": "More Verilog Features", "adder100i": "More Verilog Features",
            "bcdadd100": "More Verilog Features",
            
            # Basic Gates (17)
            "gates": "Basic Gates", "7420": "Basic Gates",
            "truthtable1": "Basic Gates", "mt2015_eq2": "Basic Gates",
            "mt2015_q4a": "Basic Gates", "mt2015_q4b": "Basic Gates",
            "mt2015_q4": "Basic Gates", "ringer": "Basic Gates",
            "thermostat": "Basic Gates", "popcount3": "Basic Gates",
            "gatesv": "Basic Gates", "gatesv100": "Basic Gates",
            "exams/m2014_q4h": "Basic Gates", "exams/m2014_q4i": "Basic Gates",
            "exams/m2014_q4e": "Basic Gates", "exams/m2014_q4f": "Basic Gates",
            "exams/m2014_q4g": "Basic Gates",
            
            # Multiplexers (5)
            "mux2to1": "Multiplexers", "mux2to1v": "Multiplexers",
            "mux9to1v": "Multiplexers", "mux256to1": "Multiplexers",
            "mux256to1v": "Multiplexers",
            
            # Arithmetic Circuits (7)
            "hadd": "Arithmetic Circuits", "fadd": "Arithmetic Circuits",
            "adder3": "Arithmetic Circuits", "adder100": "Arithmetic Circuits",
            "bcdadd4": "Arithmetic Circuits",
            "exams/m2014_q4j": "Arithmetic Circuits",
            "exams/ece241_2014_q1c": "Arithmetic Circuits",
            
            # Karnaugh Map (8)
            "kmap1": "Karnaugh Map to Circuit", "kmap2": "Karnaugh Map to Circuit",
            "kmap3": "Karnaugh Map to Circuit", "kmap4": "Karnaugh Map to Circuit",
            "exams/ece241_2013_q2": "Karnaugh Map to Circuit",
            "exams/m2014_q3": "Karnaugh Map to Circuit",
            "exams/2012_q1g": "Karnaugh Map to Circuit",
            "exams/ece241_2014_q3": "Karnaugh Map to Circuit",
            
            # Latches and Flip-Flops (18)
            "dff": "Latches and Flip-Flops", "dff8": "Latches and Flip-Flops",
            "dff8r": "Latches and Flip-Flops", "dff8p": "Latches and Flip-Flops",
            "dff8ar": "Latches and Flip-Flops", "dff16e": "Latches and Flip-Flops",
            "edgedetect": "Latches and Flip-Flops", "edgedetect2": "Latches and Flip-Flops",
            "edgecapture": "Latches and Flip-Flops", "dualedge": "Latches and Flip-Flops",
            "exams/m2014_q4a": "Latches and Flip-Flops",
            "exams/m2014_q4b": "Latches and Flip-Flops",
            "exams/m2014_q4c": "Latches and Flip-Flops",
            "exams/m2014_q4d": "Latches and Flip-Flops",
            "mt2015_muxdff": "Latches and Flip-Flops",
            "exams/2014_q4a": "Latches and Flip-Flops",
            "exams/ece241_2014_q4": "Latches and Flip-Flops",
            "exams/ece241_2013_q7": "Latches and Flip-Flops",
            
            # Counters (8)
            "count15": "Counters", "count10": "Counters", "count1to10": "Counters",
            "countslow": "Counters", "countbcd": "Counters", "count_clock": "Counters",
            "exams/ece241_2014_q7a": "Counters", "exams/ece241_2014_q7b": "Counters",
            
            # Shift Registers (9)
            "shift4": "Shift Registers", "rotate100": "Shift Registers",
            "shift18": "Shift Registers", "lfsr5": "Shift Registers",
            "mt2015_lfsr": "Shift Registers", "lfsr32": "Shift Registers",
            "exams/m2014_q4k": "Shift Registers", "exams/2014_q4b": "Shift Registers",
            "exams/ece241_2013_q12": "Shift Registers",
            
            # More Circuits (3)
            "rule90": "More Circuits", "rule110": "More Circuits", "conwaylife": "More Circuits",
            
            # Finite State Machines (33)
            "fsm1": "Finite State Machines", "fsm1s": "Finite State Machines",
            "fsm2": "Finite State Machines", "fsm2s": "Finite State Machines",
            "fsm3comb": "Finite State Machines", "fsm3onehot": "Finite State Machines",
            "fsm3": "Finite State Machines", "fsm3s": "Finite State Machines",
            "lemmings1": "Finite State Machines", "lemmings2": "Finite State Machines",
            "lemmings3": "Finite State Machines", "lemmings4": "Finite State Machines",
            "fsm_onehot": "Finite State Machines", "fsm_ps2": "Finite State Machines",
            "fsm_ps2data": "Finite State Machines", "fsm_serial": "Finite State Machines",
            "fsm_serialdata": "Finite State Machines", "fsm_serialdp": "Finite State Machines",
            "fsm_hdlc": "Finite State Machines",
            "exams/ece241_2013_q4": "Finite State Machines",
            "exams/ece241_2013_q8": "Finite State Machines",
            "exams/ece241_2014_q5a": "Finite State Machines",
            "exams/ece241_2014_q5b": "Finite State Machines",
            "exams/2014_q3fsm": "Finite State Machines",
            "exams/2014_q3bfsm": "Finite State Machines",
            "exams/2014_q3c": "Finite State Machines",
            "exams/m2014_q6b": "Finite State Machines",
            "exams/m2014_q6c": "Finite State Machines",
            "exams/m2014_q6": "Finite State Machines",
            "exams/2012_q2fsm": "Finite State Machines",
            "exams/2012_q2b": "Finite State Machines",
            "exams/2013_q2afsm": "Finite State Machines",
            "exams/2013_q2bfsm": "Finite State Machines",
            
            # Building Larger Circuits (7)
            "exams/review2015_count1k": "Building Larger Circuits",
            "exams/review2015_shiftcount": "Building Larger Circuits",
            "exams/review2015_fsmseq": "Building Larger Circuits",
            "exams/review2015_fsmshift": "Building Larger Circuits",
            "exams/review2015_fsm": "Building Larger Circuits",
            "exams/review2015_fancytimer": "Building Larger Circuits",
            "exams/review2015_fsmonehot": "Building Larger Circuits",
            
            # Verification (5+10+5)
            "bugs_mux2": "Finding bugs in code", "bugs_nand3": "Finding bugs in code",
            "bugs_mux4": "Finding bugs in code", "bugs_addsubz": "Finding bugs in code",
            "bugs_case": "Finding bugs in code",
            "sim/circuit1": "Build from waveform", "sim/circuit2": "Build from waveform",
            "sim/circuit3": "Build from waveform", "sim/circuit4": "Build from waveform",
            "sim/circuit5": "Build from waveform", "sim/circuit6": "Build from waveform",
            "sim/circuit7": "Build from waveform", "sim/circuit8": "Build from waveform",
            "sim/circuit9": "Build from waveform", "sim/circuit10": "Build from waveform",
            "tb/clock": "Writing Testbenches", "tb/tb1": "Writing Testbenches",
            "tb/and": "Writing Testbenches", "tb/tb2": "Writing Testbenches",
            "tb/tff": "Writing Testbenches",
            
            # CS450 (4)
            "cs450/timer": "CS450", "cs450/counter_2bc": "CS450",
            "cs450/history_shift": "CS450", "cs450/gshare": "CS450",
        }
        
        # 直接匹配
        if clean in PROBLEM_MAP:
            return PROBLEM_MAP[clean]
        
        # 尝试去掉 exams/ 前缀匹配
        for key, chapter in PROBLEM_MAP.items():
            if key.endswith(clean) or clean.endswith(key.split('/')[-1]):
                return chapter
        
        return "Unknown"
    
    # ========== 修复2：逐个题目统计到章节 ==========
    chapter_done = {}
    unknown_problems = []
    
    for day in data["daily"]:
        for p in day.get("problems", []):
            ch = get_chapter_from_problem(p)
            if ch != "Unknown":
                chapter_done[ch] = chapter_done.get(ch, 0) + 1
            else:
                unknown_problems.append(p)
    
    # 统计
    total_done = sum(chapter_done.values())
    unique_days = len(set(d["date"] for d in data["daily"]))
    avg = total_done / unique_days if unique_days > 0 else 0
    
    # 生成阶段/章节 HTML
    phases_html = ""
    for phase in plan["phases"]:
        # 计算该阶段完成度
        phase_chapters_done = {}
        phase_total_done = 0
        phase_total_plan = 0
        
        for ch in phase["chapters"]:
            done = chapter_done.get(ch["name"], 0)
            phase_chapters_done[ch["name"]] = done
            phase_total_done += done
            phase_total_plan += ch["problems"]
        
        phase_pct = (phase_total_done / phase_total_plan * 100) if phase_total_plan > 0 else 0
        
        # 判断状态
        if phase_total_done >= phase_total_plan:
            status_color = "#3fb950"  # 绿色完成
            status_text = "✅ 完成"
        elif phase_pct > 0:
            status_color = "#58a6ff"  # 蓝色进行中
            status_text = f"🟢 {phase_pct:.0f}%"
        else:
            status_color = "#8b949e"  # 灰色未开始
            status_text = "⚪ 未开始"
        
        # 章节详情
        chapters_detail = ""
        for ch in phase["chapters"]:
            done = phase_chapters_done.get(ch["name"], 0)
            total = ch["problems"]
            pct = (done / total * 100) if total > 0 else 0
            
            # 进度条颜色
            if done >= total:
                bar_color = "#238636"
                icon = "✅"
            elif pct > 0:
                bar_color = "#58a6ff"
                icon = "🟢"
            else:
                bar_color = "#30363d"
                icon = "⚪"
            
            chapters_detail += f'''
            <div style="background: #0d1117; padding: 12px; border-radius: 6px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 14px; color: #c9d1d9;">{ch["name"]}</span>
                    <span style="font-size: 13px; color: #8b949e;">{icon} {done}/{total}</span>
                </div>
                <div style="height: 6px; background: #21262d; border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; width: {min(100, pct)}%; background: {bar_color}; border-radius: 3px; transition: width 0.3s;"></div>
                </div>
            </div>
            '''
        
        phases_html += f'''
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 20px; border-left: 4px solid {status_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div>
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 2px;">{phase["category"]}</div>
                    <div style="font-size: 16px; font-weight: 600; color: #f0f6fc;">{phase["name"]}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 18px; font-weight: 700; color: {status_color};">{status_text}</div>
                    <div style="font-size: 12px; color: #8b949e;">{phase_total_done}/{phase_total_plan} 题</div>
                </div>
            </div>
            <div style="height: 8px; background: #21262d; border-radius: 4px; margin-bottom: 16px; overflow: hidden;">
                <div style="height: 100%; width: {min(100, phase_pct)}%; background: linear-gradient(90deg, {status_color}, {status_color}aa); border-radius: 4px;"></div>
            </div>
            {chapters_detail}
        </div>
        '''
    
    # 最近记录（去重显示）
    recent_records = ""
    for d in reversed(data["daily"][-10:]):
        chapters_str = ", ".join(d.get("chapters", ["Unknown"]))
        problems_str = ", ".join(d.get("problems", [])[:5])
        if len(d.get("problems", [])) > 5:
            problems_str += f" ...+{len(d['problems'])-5}题"
        
        recent_records += f'''
        <tr style="border-bottom: 1px solid #21262d;">
            <td style="padding: 10px 8px; font-size: 13px; color: #c9d1d9;">{d['date']}</td>
            <td style="padding: 10px 8px; font-size: 13px; color: #58a6ff;">{chapters_str}</td>
            <td style="padding: 10px 8px; font-size: 13px; color: #8b949e;">{d['done']}/{d['planned']}</td>
            <td style="padding: 10px 8px; font-size: 12px; color: #c9d1d9; max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{problems_str}</td>
        </tr>
        '''
    
    # 生成完整HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HDLBits 刷题进度</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
            background: #0d1117; 
            color: #c9d1d9; 
            line-height: 1.6;
        }}
        #login {{ 
            text-align: center; 
            padding-top: 150px; 
            min-height: 100vh;
            background: #0d1117;
        }}
        #login h2 {{ color: #f0f6fc; margin-bottom: 20px; font-size: 24px; }}
        #login input {{ 
            padding: 12px 16px; 
            font-size: 16px; 
            border: 1px solid #30363d; 
            background: #21262d; 
            color: white; 
            border-radius: 6px; 
            width: 250px;
            margin-bottom: 10px;
        }}
        #login button {{ 
            padding: 12px 24px; 
            background: #238636; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 600;
            font-size: 14px;
        }}
        #login button:hover {{ background: #2ea043; }}
        .hidden {{ display: none; }}
        
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}
        
        h1 {{ 
            color: #f0f6fc; 
            font-size: 28px; 
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 1px solid #30363d;
        }}
        
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 16px; 
            margin-bottom: 32px; 
        }}
        .stat-card {{ 
            background: #161b22; 
            border: 1px solid #30363d; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center;
        }}
        .stat-value {{ 
            font-size: 32px; 
            font-weight: 700; 
            color: #58a6ff; 
            margin-bottom: 4px;
        }}
        .stat-label {{ 
            font-size: 13px; 
            color: #8b949e; 
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .section-title {{
            font-size: 20px;
            color: #f0f6fc;
            margin: 32px 0 16px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #0d1117;
            padding: 12px;
            text-align: left;
            font-size: 12px;
            color: #8b949e;
            text-transform: uppercase;
            font-weight: 600;
            border-bottom: 1px solid #30363d;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #21262d;
        }}
        
        .warning {{
            background: #f8514920;
            border: 1px solid #f85149;
            color: #f85149;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div id="login">
        <h2>🔒 HDLBits Tracker</h2>
        <p style="color: #8b949e; margin-bottom: 20px;">请输入访问密码</p>
        <input type="password" id="pwd" placeholder="password" onkeypress="if(event.key==='Enter')check()">
        <br>
        <button onclick="check()">进入</button>
        <p id="error" style="color: #f85149; display: none; margin-top: 10px;">密码错误</p>
    </div>

    <div id="content" class="hidden">
        <div class="container">
            <h1>HDLBits 刷题进度</h1>
            
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
                    <div class="stat-value">{len([c for c in chapter_done.values() if c > 0])}</div>
                    <div class="stat-label">已开始章节</div>
                </div>
            </div>
            
            {'<div class="warning">⚠️ 以下题目未识别章节：' + ", ".join(set(unknown_problems)) + '</div>' if unknown_problems else ''}
            
            <div class="section-title">📚 章节进度</div>
            {phases_html}
            
            <div class="section-title">📝 最近记录</div>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>章节</th>
                        <th>完成</th>
                        <th>题目</th>
                    </tr>
                </thead>
                <tbody>
                    {recent_records}
                </tbody>
            </table>
        </div>
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
    print(f"✅ 已生成修复版网站")
    if unknown_problems:
        print(f"⚠️ 未识别题目：{set(unknown_problems)}")
    print(f"📊 统计：{total_done}题，分布在 {len(chapter_done)} 个章节")

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