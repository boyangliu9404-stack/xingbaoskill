import argparse
import datetime as _dt
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZODIAC = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]


SUN_SIGNS = [
    ((1, 20), "水瓶座"),
    ((2, 19), "双鱼座"),
    ((3, 21), "白羊座"),
    ((4, 20), "金牛座"),
    ((5, 21), "双子座"),
    ((6, 22), "巨蟹座"),
    ((7, 23), "狮子座"),
    ((8, 23), "处女座"),
    ((9, 23), "天秤座"),
    ((10, 24), "天蝎座"),
    ((11, 23), "射手座"),
    ((12, 22), "摩羯座"),
]

if hasattr(sys.stdout, "reconfigure"):
    # Improve Chinese output on Windows terminals.
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def _read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def ganzhi_year(year: int) -> str:
    # 1984 is 甲子
    offset = year - 1984
    return f"{STEMS[offset % 10]}{BRANCHES[offset % 12]}"


def chinese_zodiac(year: int) -> str:
    # 1984 is 鼠
    offset = year - 1984
    return ZODIAC[offset % 12]


def sun_sign(month: int, day: int) -> str:
    # Using common tropical zodiac date ranges (not considering timezone/precise cusp).
    for (m, d), name in SUN_SIGNS:
        if (month, day) < (m, d):
            # previous sign
            idx = SUN_SIGNS.index(((m, d), name)) - 1
            return SUN_SIGNS[idx][1]
    return "摩羯座"


def _prompt(label: str, optional: bool = False) -> str:
    while True:
        val = input(label).strip()
        if val:
            return val
        if optional:
            return ""


def _parse_date(s: str) -> _dt.date:
    s = s.strip().replace("/", "-").replace(".", "-")
    return _dt.date.fromisoformat(s)


def _parse_time(s: str) -> _dt.time:
    s = s.strip()
    if ":" not in s:
        return _dt.time(int(s), 0)
    hh, mm = s.split(":", 1)
    return _dt.time(int(hh), int(mm))


@dataclass
class UserProfile:
    birth_date: _dt.date
    birth_time: _dt.time
    city: str
    gender: str
    mbti: str = ""
    issue: str = ""


def classify_issue(text: str) -> str:
    t = text.lower()
    career = ["工作", "职业", "转型", "跳槽", "升职", "面试", "简历", "创业", "裁员", "倦怠", "薪", "offer"]
    relationship = ["感情", "恋爱", "分手", "婚姻", "伴侣", "出轨", "暧昧", "相亲", "冷战", "沟通"]
    growth = ["焦虑", "抑郁", "成长", "自律", "拖延", "迷茫", "意义", "学习", "习惯", "压力", "情绪"]
    if any(k in text for k in career) or any(k in t for k in ["career", "job"]):
        return "career"
    if any(k in text for k in relationship) or any(k in t for k in ["relationship", "love"]):
        return "relationship"
    if any(k in text for k in growth):
        return "growth"
    return "general"


def print_header() -> None:
    print("🌟 你好呀！我是星宝～（本地测试版）")
    print("说明：这是一个离线的交互壳，用来在本地“跑通 Skill 流程”。")
    print("提示：没有接入万年历/星历工具时，我只会给高确定性信息，其余用“可能/倾向”描述。\n")


def step1_collect() -> UserProfile:
    print("### Step 1：信息解析与数据准备\n")
    bd = _parse_date(_prompt("出生日期（YYYY-MM-DD）："))
    bt = _parse_time(_prompt("出生时间（HH 或 HH:MM，尽量准确）："))
    city = _prompt("出生地点（城市）：")
    gender = _prompt("性别（男/女/其他）：")
    issue = _prompt("当前困惑（可选）：", optional=True)
    mbti = _prompt("已知 MBTI（可选，例如 INTJ）：", optional=True)
    return UserProfile(birth_date=bd, birth_time=bt, city=city, gender=gender, issue=issue, mbti=mbti)


def step1_confirm(p: UserProfile) -> None:
    y = p.birth_date.year
    ssign = sun_sign(p.birth_date.month, p.birth_date.day)
    print("\n我已收到你的信息，先帮你做个确认：")
    print(f"- 出生：{p.birth_date.isoformat()} {p.birth_time.strftime('%H:%M')}（{p.city}）")
    print(f"- 性别：{p.gender}")
    if p.issue:
        print(f"- 当前困惑：{p.issue}")
    if p.mbti:
        print(f"- MBTI：{p.mbti}")
    print("\n我将开始做综合分析（离线版会以“趋势/参考”为主）。")
    print("\n【可高确定性计算】")
    print(f"- 生肖（按公历年粗略）：{chinese_zodiac(y)}")
    print(f"- 年柱（按公历年粗略）：{ganzhi_year(y)}年")
    print(f"- 太阳星座：{ssign}")
    print("\n【需要工具/精确排盘】")
    print("- 四柱中的月柱/日柱/时柱：需要节气与历法工具精确计算")
    print("- 月亮星座/上升星座/宫位/相位：需要星历工具精确计算\n")


def step6_goal_clarify(existing_issue: str) -> Tuple[str, str, str, str]:
    print("### Step 6：目标澄清多轮对话（离线问答）\n")
    if existing_issue:
        print("我先复述一下你刚才的困惑，看看我理解得对不对：")
        print(f"“{existing_issue}”\n")
    trouble = _prompt("最近最困扰你的具体问题是什么？（一句话也可以）：")
    work6 = _prompt("如果看接下来的半年，在工作/学业上你希望达到什么状态？：")
    life6 = _prompt("生活方面呢？半年后你希望自己过着什么样的生活？：")
    long35 = _prompt("把眼光放远一点（3-5 年），你想成为什么样的人？：")
    print("\n让我确认一下我理解的要点：")
    print(f"- 当前困扰：{trouble}")
    print(f"- 半年目标（工作/学业）：{work6}")
    print(f"- 半年目标（生活）：{life6}")
    print(f"- 长期愿景（3-5 年）：{long35}\n")
    return trouble, work6, life6, long35


def _plan_career(trouble: str, work6: str) -> str:
    return f"""🎯 你的3个月行动计划（职业/转型方向，离线模板）

【核心目标（3个月）】
- 将“{work6}”拆成可验证的小步，并在 12 周内完成一次方向验证与一次真实行动（投递/面试/副业试水/项目发布等）。

【月度里程碑】
📅 第一个月：探索与验证
- 访谈 3 位目标方向从业者（或做 3 次信息访谈）
- 产出 1 份方向对比表（选项、代价、收益、下一步）
- 做一次“低成本试水”（例如 1 个小项目/1 次公开输出）

📅 第二个月：能力准备与作品化
- 完成 1 个可展示的作品/项目（可写成案例）
- 补齐 1-2 个关键技能点（课程/练习/实战）
- 扩展人脉：加入 1 个相关社群并做一次有效连接

📅 第三个月：行动与决策
- 对外行动：投递/面试/谈合作/上线产品（至少完成一项）
- 复盘：你在“{trouble}”里真正需要的是什么（自主/成长/安全感/影响力等）
- 做一个明确决策：继续/调整/停止某条路径

【本周行动清单（3-5项）】
☐ 列出 10 个你想尝试的方向/岗位关键词（完成标准：能用于搜索职位/人脉）
☐ 约 1 次信息访谈（完成标准：确定时间+准备 5 个问题）
☐ 写 1 段自我介绍/转型叙事（完成标准：200-400 字可复用）
"""


def _plan_relationship(trouble: str) -> str:
    return f"""🎯 你的3个月行动计划（关系/情感方向，离线模板）

【核心目标（3个月）】
- 把“{trouble}”从“反复内耗”推进到“看清需求—建立边界—做出选择”。

【月度里程碑】
📅 第一个月：看清自己
- 写 10 条“我在关系中最在意/最害怕的是什么”
- 梳理 3 个触发点（什么时候最容易争吵/冷战/失控）
- 做一次关键沟通（不追求结论，先追求对齐）

📅 第二个月：练习边界与沟通
- 为 2 个高频冲突场景准备沟通脚本
- 练习 2 次“提出请求 + 接受不同答案”
- 如果需要，寻找外部支持（咨询/书/课程）

📅 第三个月：评估与决定
- 明确关系是否满足你的核心需求（至少 3 条）
- 做一个具体决定（继续投入、调整相处、暂停或结束）

【本周行动清单（3-5项）】
☐ 写下你最想被理解的 3 句话（完成标准：具体可说出口）
☐ 给对方/自己提出 1 个可执行的小请求（完成标准：有时间点）
☐ 记录一次冲突的“事实-感受-需求-请求”（完成标准：写完四段）
"""


def _plan_growth(trouble: str) -> str:
    return f"""🎯 你的3个月行动计划（个人成长/情绪方向，离线模板）

【核心目标（3个月）】
- 把“{trouble}”从“被情绪/习惯牵着走”推进到“更稳定的节奏 + 可持续的小系统”。

【月度里程碑】
📅 第一个月：建立基线
- 固定一条最小习惯（每天 10 分钟也算）
- 记录 14 天能量曲线（何时最有精神/最容易低落）
- 找到 1 个能明显降低压力的动作（散步/呼吸/整理）

📅 第二个月：投入与产出
- 每周 3 次 45-90 分钟深度投入（学习/创作/运动其一）
- 把一个主题做成可展示产出（笔记/作品/计划表）

📅 第三个月：巩固与迭代
- 复盘：哪些做法真的有效，哪些只是自责
- 形成你的“复位清单”（低谷时先做哪三件事）

【本周行动清单（3-5项）】
☐ 选 1 条最小习惯并设定触发点（完成标准：写在日历/待办里）
☐ 做 1 次 30 分钟的无干扰投入（完成标准：计时完成）
☐ 写 1 段复盘：本周让我更轻松的 1 件事（完成标准：100 字）
"""


def step7_plan(trouble: str, work6: str, issue_text: str, *, interactive: bool = True) -> None:
    print("### Step 7：行动方案制定（离线模板）\n")
    kind = classify_issue(issue_text + " " + trouble + " " + work6)
    if kind == "career":
        print(_plan_career(trouble, work6))
    elif kind == "relationship":
        print(_plan_relationship(trouble))
    elif kind == "growth":
        print(_plan_growth(trouble))
    else:
        print(_plan_growth(trouble))
    if interactive and getattr(sys.stdin, "isatty", lambda: True)():
        print("【承诺确认】")
        _ = _prompt("你愿意为本周行动清单打几分（1-10）？：")
    else:
        print("【承诺确认】（demo/非交互模式已跳过）")
    print("\n好的～你随时可以在本地再次运行，并用“星宝我来啦”开启回访。\n")


def cmd_chat(_args: argparse.Namespace) -> int:
    print_header()
    p = step1_collect()
    step1_confirm(p)
    trouble, work6, life6, long35 = step6_goal_clarify(p.issue)
    _ = (life6, long35)  # kept for future扩展
    step7_plan(trouble, work6, p.issue, interactive=True)
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    spec = Path(args.spec).resolve()
    if not spec.exists():
        print(f"未找到 Skill 文件：{spec}")
        return 2
    print(_read_text(spec))
    return 0


def cmd_demo(_args: argparse.Namespace) -> int:
    print_header()
    p = UserProfile(
        birth_date=_dt.date(1990, 8, 15),
        birth_time=_dt.time(14, 0),
        city="北京",
        gender="女",
        issue="工作遇到瓶颈，想转型但不知道方向",
        mbti="ENTJ",
    )
    step1_confirm(p)
    trouble, work6, life6, long35 = (
        "工作倦怠，想转型但担心风险",
        "开始验证一个更适合我的方向，并拿到一个明确机会/成果",
        "拥有更稳定的作息与更多个人时间",
        "成为能影响他人、做长期价值的人",
    )
    _ = (life6, long35)
    print("### Step 6：目标澄清多轮对话（Demo）\n")
    print(f"- 当前困扰：{trouble}")
    print(f"- 半年目标（工作/学业）：{work6}")
    print(f"- 半年目标（生活）：{life6}")
    print(f"- 长期愿景（3-5 年）：{long35}\n")
    step7_plan(trouble, work6, p.issue, interactive=False)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="xiaobaoskill", description="星宝 Skill 本地交互壳（离线版）")
    sub = p.add_subparsers(dest="cmd")

    chat = sub.add_parser("chat", help="交互式跑通 Step 1/6/7（离线模板）")
    chat.set_defaults(func=cmd_chat)

    pr = sub.add_parser("prompt", help="打印 SKILL.md 便于复制到平台")
    pr.add_argument("--spec", default=str(Path(__file__).with_name("SKILL.md")), help="Skill 文件路径（默认 ./SKILL.md）")
    pr.set_defaults(func=cmd_prompt)

    demo = sub.add_parser("demo", help="免输入演示一次完整流程")
    demo.set_defaults(func=cmd_demo)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        # Default to chat for “运行 xiaobaoskill”
        return cmd_chat(args)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

