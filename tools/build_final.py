"""Build the final bank: official 本科 chapter structure, voted answers, CSV export."""

import collections
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def nz(s):
    return re.sub(r"[\W_]+", "", s or "", flags=re.UNICODE)


def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except FileNotFoundError:
        return []


CHAPTERS = [
    (
        "01",
        "市场调查概述",
        [
            "市场调查", "市场调研", "营销决策", "调查问题", "决策问题", "探索性",
            "描述性研究", "因果性", "预测性", "调查功能", "调查作用", "调查原则",
            "调查特点", "调查分类", "调查类型", "营销信息系统", "竞争情报",
            "基本程序", "调查程序", "应用范围", "宏观环境", "微观环境", "市场研究",
            "供应分析", "需求分析", "促销调查", "产品调查", "营销实务", "市场细分",
            "竞争对手", "购买动机", "购买行为", "广告曝光", "广告媒体", "市场商品",
            "企业受市场", "商场对客流", "产品实体", "产品包装", "产品生命周期",
        ],
        [
            ("基本概念与作用", ["市场调查", "市场调研", "功能", "作用", "原则", "特点", "营销"]),
            ("调查基本程序", ["程序", "步骤", "环节", "过程"]),
            ("调查类型", ["探索性", "描述性", "因果性", "预测性", "分类", "类型"]),
            ("环境与情报", ["环境", "竞争情报", "信息系统", "宏观", "微观"]),
            ("调查内容与市场细分", ["市场细分", "营销实务", "供应分析", "需求分析", "购买动机", "购买行为", "广告", "竞争对手"]),
        ],
    ),
    (
        "02",
        "数据收集",
        [
            "访问", "访谈", "座谈", "焦点小组", "深度访谈", "观察法", "实验法",
            "实验设计", "电话调查", "邮寄调查", "网络调查", "入户", "拦访", "街访",
            "神秘顾客", "神秘购物", "投射", "投影技法", "二手数据", "案头", "文案调查",
            "定性", "定量", "调查员", "督导", "CATI", "CAPI", "CAWI", "日记法",
            "德尔菲", "头脑风暴", "专家", "抽样框", "调查组织", "项目组", "组织实施",
            "进度", "预算", "费用", "质量控制", "培训", "回收率", "回答率",
            "观察", "投影法", "代理回答", "回访", "乱数", "完全随机设计", "APP",
            "直线式", "职能式", "矩阵式", "调查提供者", "委托人", "索取法",
        ],
        [
            ("定性数据收集", ["定性", "深度访谈", "座谈", "焦点小组", "投射", "投影", "观察法", "德尔菲", "头脑风暴"]),
            ("定量数据收集", ["定量", "电话", "邮寄", "网络调查", "入户", "拦访", "街访", "CATI", "CAPI", "CAWI", "实验", "日记"]),
            ("一手与二手数据", ["二手", "案头", "文案", "一手", "原始"]),
            ("组织实施与质量控制", ["组织", "督导", "调查员", "培训", "质量", "进度", "预算", "费用", "回收"]),
        ],
    ),
    (
        "03",
        "调查设计",
        [
            "调查方案", "设计方案", "调查计划", "策划", "研究设计", "调查对象",
            "调查单位", "报告单位", "调查项目", "调查方式", "调查表", "调查时间",
            "调查期限", "方案内容", "可行性",
            "调查目标", "调查目的", "调查内容",
        ],
        [
            ("方案结构与内容", ["方案", "内容", "策划", "计划"]),
            ("调查对象与单位", ["调查对象", "调查单位", "报告单位", "调查项目"]),
            ("调查方式选择", ["调查方式", "调查表", "时间", "期限"]),
        ],
    ),
    (
        "04",
        "问卷与量表",
        [
            "问卷", "量表", "李克特", "瑟斯顿", "语义差异", "封闭式", "开放式",
            "封闭题", "开放题", "题型", "提问", "措辞", "预调查", "试访", "甄别",
            "等级顺序", "评比量表", "Q分类", "信度", "效度", "测量尺度", "定类",
            "定序", "定距", "定比", "名义尺度", "顺序尺度", "等距尺度", "比率尺度",
            "问句", "表述不清晰", "时间限定", "选项设计", "排序法", "过滤法",
            "计量尺度", "顺序效应", "问题排列",
        ],
        [
            ("问卷结构", ["结构", "甄别", "背景", "开头", "问候", "指导语"]),
            ("问题与选项设计", ["问句", "提问", "措辞", "表述", "选项", "开放", "封闭", "排序", "过滤", "敏感"]),
            ("量表类型", ["量表", "李克特", "瑟斯顿", "语义差异", "Q分类", "等级", "评比"]),
            ("测量尺度", ["测量尺度", "定类", "定序", "定距", "定比", "名义", "顺序", "等距", "比率"]),
            ("信度与效度", ["信度", "效度", "预调查", "试访"]),
        ],
    ),
    (
        "05",
        "数据处理与报告",
        [
            "编码", "插补", "数据清洁", "数据清理", "审核", "逻辑检查", "计算检查",
            "编辑", "录入", "数据仓库", "数据仓储", "检索", "无回答", "缺失", "有效问卷",
            "汇总", "制表", "统计表", "调查报告", "报告撰写", "报告结构", "撰写",
            "书面报告", "口头报告", "演示",
            "预处理", "原始信息", "原始记录", "数据清洁",
        ],
        [
            ("数据审核与清理", ["审核", "逻辑检查", "计算检查", "清洁", "清理", "编辑", "录入"]),
            ("编码与插补", ["编码", "插补", "缺失", "无回答"]),
            ("汇总与制表", ["汇总", "制表", "统计表", "数据仓库", "检索"]),
            ("报告撰写", ["调查报告", "撰写", "报告结构", "演示", "口头", "书面"]),
        ],
    ),
    (
        "06",
        "单变量分析",
        [
            "众数", "中位数", "均值", "平均数", "标准差", "方差", "极差", "四分位",
            "离散系数", "变异系数", "偏度", "峰度", "偏态", "直方图", "茎叶图",
            "箱线图", "条形图", "饼图", "折线图", "频数", "频率", "分组", "组距",
            "组中值", "累计", "集中趋势", "离中趋势", "描述统计", "平均差",
            "离散程度", "时点数列", "时期数列", "时间数列", "动态数列", "发展速度",
            "增长速度", "环比", "同比", "移动平均", "季节", "趋势", "指数",
            "置信区间", "置信度", "显著性水平", "假设检验", "原假设", "备择假设",
            "第一类错误", "第二类错误", "拒绝域", "p值", "P值", "检验统计量",
            "点估计", "区间估计", "无偏", "有效性", "一致性", "充分性",
            "中心极限定理", "标准误", "自由度", "差异性", "集中度", "规模",
            "结构分析", "比较分析", "综合指数", "平均指标", "相对指标",
            "序列", "图形", "班级", "成绩", "产值", "平均增长", "利润计划",
            "进展速度", "平均人数", "加权处理", "三维透视", "时点", "时期",
        ],
        [
            ("参数估计", ["置信区间", "置信度", "点估计", "区间估计", "无偏", "有效性", "一致性", "充分性", "标准误", "中心极限"]),
            ("显著性检验", ["假设检验", "原假设", "备择假设", "第一类错误", "第二类错误", "拒绝域", "p值", "P值", "检验统计量", "显著性水平", "自由度", "差异性", "Z检验", "t检验", "F检验", "卡方检验", "χ2检验", "检验"]),
            ("集中趋势", ["众数", "中位数", "均值", "平均数", "集中趋势", "平均指标"]),
            ("离散程度", ["标准差", "方差", "极差", "四分位", "离散", "变异", "平均差", "离中"]),
            ("分布形态与图表", ["偏度", "峰度", "偏态", "直方图", "茎叶图", "箱线图", "条形图", "饼图", "折线图", "频数", "分组", "组距"]),
            ("时间数列", ["时间数列", "动态数列", "时点", "时期", "发展速度", "增长速度", "环比", "同比", "移动平均", "季节", "趋势"]),
            ("规模结构与比较", ["规模", "结构", "比较", "集中度", "综合指数", "相对指标"]),
        ],
    ),
    (
        "07",
        "抽样估计",
        [
            "抽样", "样本", "总体", "抽样框", "抽样误差", "非抽样误差", "分层",
            "整群", "系统抽样", "等距抽样", "简单随机", "多阶段", "PPS", "二重抽样",
            "样本量", "样本容量", "估计量", "估计值", "抽样方案", "抽样效率",
            "滚雪球", "配额", "判断抽样", "方便抽样", "雪球", "随机原则", "抽样单元",
            "乱数表",
        ],
        [
            ("抽样设计", ["抽样框", "分层", "整群", "系统", "等距", "简单随机", "多阶段", "PPS", "二重", "滚雪球", "配额", "判断抽样", "方便", "方案"]),
            ("样本量与误差", ["样本量", "样本容量", "抽样误差", "非抽样误差", "效率", "精度"]),
            ("抽样估计", ["估计量", "估计值", "推断", "总体参数"]),
        ],
    ),
    (
        "08",
        "双变量关联分析",
        [
            "回归", "相关系数", "相关分析", "列联表", "卡方检验", "χ2", "χ²",
            "交叉表", "散点图", "最小二乘", "决定系数", "拟合优度", "方差分析",
            "ANOVA", "协方差分析", "t检验", "F检验", "相关关系", "函数关系",
            "正相关", "负相关", "残差", "多重共线性", "自相关", "异方差",
        ],
        [
            ("列联分析", ["列联", "卡方", "χ2", "χ²", "交叉表", "拟合优度"]),
            ("相关分析", ["相关", "散点图", "相关系数"]),
            ("回归分析", ["回归", "最小二乘", "决定系数", "残差", "共线性", "异方差", "自相关", "估计标准误"]),
            ("方差分析", ["方差分析", "ANOVA", "协方差"]),
        ],
    ),
    (
        "09",
        "多变量分析（一）",
        [
            "多变量方差", "MANOVA", "Wilks", "多变量回归", "多元回归", "多元相关",
            "Logistic", "logistic", "逻辑回归", "判别分析", "判别", "Fisher", "马氏距离",
            "多变量分析", "多元分析",
        ],
        [
            ("多变量方差分析", ["多变量方差", "MANOVA", "Wilks"]),
            ("多变量相关与回归", ["多元回归", "多元相关", "多变量回归"]),
            ("Logistic 模型", ["Logistic", "logistic", "逻辑回归"]),
            ("判别分析", ["判别", "Fisher", "马氏距离", "距离判别"]),
        ],
    ),
    (
        "10",
        "多变量分析（二）",
        [
            "因子分析", "主成分", "聚类分析", "聚类", "对应分析", "多维标度",
            "联合分析", "综合评价", "KMO", "Bartlett", "因子载荷", "旋转",
            "特征值", "碎石图", "路径分析", "结构方程",
            "评价指标体系", "无量纲",
        ],
        [
            ("因子分析", ["因子", "主成分", "KMO", "Bartlett", "载荷", "旋转", "特征值", "碎石图"]),
            ("聚类分析", ["聚类", "类间", "类内"]),
            ("对应分析与多维标度", ["对应分析", "多维标度"]),
            ("联合分析与综合评价", ["联合分析", "综合评价", "权重", "指标体系"]),
            ("结构方程", ["路径分析", "结构方程"]),
        ],
    ),
    (
        "A",
        "附录A 统计学基础",
        [
            "统计学", "统计量", "统计指标", "标志值", "标志", "变量", "统计调查",
            "统计报表", "普查", "重点调查", "典型调查", "统计资料", "统计工作",
            "描述统计学", "推断统计学", "样本", "参数", "假设", "统计方法",
        ],
        [
            ("统计学基本概念", ["统计学", "描述统计学", "推断统计学", "统计方法", "核心内容"]),
            ("统计量与标志", ["统计量", "统计指标", "标志", "变量", "指标"]),
            ("统计调查方式", ["统计调查", "统计报表", "普查", "重点调查", "典型调查", "全面调查"]),
        ],
    ),
]

APPENDIX_B = (
    "B",
    "附录B 其他/超纲",
    ["招标投标", "招标", "投标", "标书", "投标人", "采购"],
    [("招投标与法规", ["招标", "投标", "采购", "法规"])],
)

ORDER = {c[0]: i for i, c in enumerate(CHAPTERS + [APPENDIX_B])}


def classify(stem, options):
    text_opt = " ".join(o[1] for o in options)
    best, best_score, best_topic = ("B", "附录B 其他/超纲"), 0.0, "未分类"
    for code, name, keywords, topics in CHAPTERS + [APPENDIX_B]:
        score = 0.0
        base_w = 2.0 if code == "01" else 3.0
        for k in keywords:
            if k in stem:
                score += base_w
            elif k in text_opt:
                score += base_w / 3.0
        if code == "A":
            # 附录 A 只在题干本身就是统计学基础时优先，避免抢走正文题目
            score = score * 0.9 if any(k in stem for k in keywords) else 0
        if score > best_score:
            best_score = score
            best = (code, name)
            topic, topic_score = "", 0
            for tname, tkw in topics:
                s = sum(3 if k in stem else (1 if k in text_opt else 0) for k in tkw)
                if s > topic_score:
                    topic, topic_score = tname, s
            if not topic:
                topic = topics[0][0]
            best_topic = topic
    return best, best_topic


SOURCES = [
    ("xlsx", load("work/xlsx_bank.json")),
    ("random", load("work/xlsx_random.json")),
    ("ed15", load("work/ed15.json")),
    ("docx", load("work/parsed_v5.json")),
]


def file_fingerprints(kind, rows):
    """Many files are byte-identical copies; give each distinct content one vote."""
    per_file = collections.defaultdict(list)
    for r in rows:
        per_file[r.get("source", "")].append((nz(r["stem"]), r["answer"]))
    seen = {}
    for f, pairs in per_file.items():
        h = hash(tuple(sorted(pairs)))
        seen.setdefault(h, []).append(f)
    # map every file name -> representative identity
    ident = {}
    for h, files in seen.items():
        canon_file = sorted(files)[0]
        for f in files:
            ident[f] = canon_file
    return ident


FILE_IDENT = {kind: file_fingerprints(kind, rows) for kind, rows in SOURCES}

# Manually verified fixups: (stem substring, required option texts, note)
OVERRIDES = [
    ("居民区共有", ["90.2"], "按 100±1.96×√(22500/900) 得 ±9.8，区间 90.2–109.8；Word 版答案有误"),
    ("估计标准误差为0", ["相关系数绝对值为1", "解释变量能解释被解释变量"], "残差为0意味着完全拟合，|r|=1"),
    ("户均月收入", ["统计量"], "样本计算值属于统计量，总体均值才是参数"),
    ("统计推断的描述", ["样本数据来推断总体", "参数估计和假设检验", "结论是不确定的"], "统计推断的核心是从样本推断总体"),
    ("二手数据的特点", ["收集程序便捷"], "二手数据省时省钱，但不是为本研究专门收集"),
    ("上限不计入", ["从高到低"], "SPSS 分组需从高到低设定界限"),
    ("不符合经济效益", ["市场普查"], "普查耗费最大，最不经济"),
    ("市场营销主体与社会公众", ["沟通功能"], "信息互相传输、交换即沟通"),
]


def clean_stem(s):
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^[\-\s]+", "", s)
    # stray option letters / answer markers that leaked into the stem
    s = re.sub(r"(\s*[A-Ea-e]){3,}$", "", s)
    s = re.sub(r"\s+[A-Ea-e]$", "", s)
    s = re.sub(r"[（(]\s*[A-Ea-e]\s*[)）]\s*[。.]?\s*$", "（ ）。", s)
    s = re.sub(r"[（(]\s*$", "", s).strip()
    return s


groups = collections.OrderedDict()
for kind, rows in SOURCES:
    for r in rows:
        k = nz(clean_stem(r["stem"]))
        if k:
            groups.setdefault(k, []).append((kind, r))

bank = []
for k, items in groups.items():
    # structural base: most options, then cleanest source
    rank = {"xlsx": 0, "random": 1, "ed15": 2, "docx": 3}
    items.sort(key=lambda x: (-len(x[1]["options"]), rank[x[0]]))
    base = dict(items[0][1])
    stem = clean_stem(base["stem"])
    opts = [[o[0], re.sub(r"\s+", " ", o[1]).strip()] for o in base["options"]]
    if len(opts) < 2 or len(stem) < 6 or len(stem) > 1200:
        continue
    if any(not o[1] or len(o[1]) > 400 for o in opts):
        continue
    text_map = {nz(o[1]): o[0] for o in opts}

    ballots = collections.defaultdict(set)  # canonical file -> set of answer-sets
    for kind, r in items:
        f = r.get("source", "")
        f = FILE_IDENT[kind].get(f, f)
        texts = []
        for ch in r["answer"]:
            i = "ABCDE".index(ch)
            if i < len(r["options"]):
                texts.append(nz(r["options"][i][1]))
        mapped = frozenset(text_map[t] for t in texts if t in text_map)
        if mapped:
            ballots[f].add(mapped)

    score = collections.Counter()
    xlsx_answers = set()
    for f, sets in ballots.items():
        for s in sets:
            score[s] += 1.0
            if f.lower().endswith(".xlsx"):
                xlsx_answers.add(s)
    if not score:
        continue
    top = score.most_common()
    best, best_score = top[0]
    tied = [s for s, v in top if v == best_score]
    if len(tied) > 1 and xlsx_answers & set(tied):
        # prefer the answer supported by the cleanest structured source
        best = sorted(xlsx_answers & set(tied), key=lambda s: sorted(s))[0]
    answer = "".join(sorted(best, key=lambda c: "ABCDE".index(c)))

    distinct_docx = len([f for f in ballots if f.lower().endswith(".txt")])
    has_clean = any(f.lower().endswith(".xlsx") for f in ballots)

    if len(score) > 1:
        confidence = "有争议" if len(tied) == 1 else "中"
    elif has_clean:
        confidence = "高"
    elif distinct_docx >= 3:
        confidence = "高"
    elif distinct_docx == 2:
        confidence = "中"
    else:
        confidence = "单源"

    # --- manually verified corrections (source banks are known to contain errors) ---
    review_note = ""
    for key, wanted_texts, note in OVERRIDES:
        if key in nz(stem):
            picked = []
            for wt in wanted_texts:
                wt_n = nz(wt)
                for t_norm, letter in text_map.items():
                    if wt_n and wt_n in t_norm and letter not in picked:
                        picked.append(letter)
                        break
            if picked:
                answer = "".join(sorted(picked, key=lambda c: "ABCDE".index(c)))
                best = frozenset(picked)
                confidence = "已核对"
                review_note = note
            break

    chapter, topic = classify(stem, opts)
    qtype = base.get("type") or ("多选" if len(best) > 1 else "单选")
    if qtype not in ("单选", "多选", "判断"):
        qtype = "多选" if len(best) > 1 else "单选"
    if len(opts) == 2 and {nz(o[1]) for o in opts} <= {nz("对"), nz("错")}:
        qtype = "判断"

    bank.append(
        {
            "id": "",
            "chapter_code": chapter[0],
            "chapter": chapter[1],
            "topic": topic,
            "type": qtype,
            "level": base.get("level", ""),
            "stem": stem,
            "options": opts,
            "answer": answer,
            "multi": len(best) > 1,
            "confidence": confidence,
            "review_note": review_note,
            "n_sources": len(ballots),
        }
    )

bank.sort(key=lambda r: (ORDER[r["chapter_code"]], r["topic"], {"单选": 0, "多选": 1, "判断": 2}[r["type"]], r["stem"]))
for i, r in enumerate(bank, 1):
    r["id"] = i

json.dump(bank, open("work/bank_release.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("total", len(bank))
print("confidence", collections.Counter(r["confidence"] for r in bank))
print("type", collections.Counter(r["type"] for r in bank))
print()
for code, name, *_ in CHAPTERS + [APPENDIX_B]:
    sub = [r for r in bank if r["chapter_code"] == code]
    print("%-4s %-18s %4d" % (code, name, len(sub)))

print("\ntopics:")
for (code, topic), n in sorted(collections.Counter((r["chapter_code"], r["topic"]) for r in bank).items()):
    print("  %-3s %-24s %4d" % (code, topic, n))
