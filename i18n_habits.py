"""
=============================================================================
🏆 ALL-IN-ONE LIFE OS : 35 Master Habits & Multilingual Keywords (4 Languages)
=============================================================================
Single source of truth for the 35 science- & mentor-backed habits across:
  - Korean (ko)
  - English (en)
  - Japanese (ja)
  - Simplified Chinese (zh)
Used by NLP/LLM matching, SQLite seeding, Floating Widget UI, Bot Bridge,
Telegram Bot, and localized Excel workbook generation.
=============================================================================
"""

from i18n import resolve_language, SUPPORTED_LANGUAGES

DOMAINS = {
    1: {
        "code": "L1",
        "gurus": {
            "ko": "워런 버핏, 피터 드러커, 일론 머스크",
            "en": "Warren Buffett, Peter Drucker, Elon Musk",
            "ja": "ウォーレン・バフェット、P・ドラッカー、イーロン・マスク",
            "zh": "沃伦·巴菲特、彼得·德鲁克、埃隆·马斯克",
        },
        "category": {
            "ko": "비즈니스/생산성",
            "en": "Business & Productivity",
            "ja": "ビジネス/生産性",
            "zh": "商业与效率",
        },
        "sheet_domain": {
            "ko": "💼 비즈니스 & 생산성",
            "en": "💼 Business & Productivity",
            "ja": "💼 ビジネス＆生産性",
            "zh": "💼 商业与效率",
        },
    },
    2: {
        "code": "L2",
        "gurus": {
            "ko": "앤드루 후버만, 르브론 제임스, 피터 아티아",
            "en": "Andrew Huberman, LeBron James, Peter Attia",
            "ja": "A・フーバーマン、レブロン・ジェームズ、P・アティア",
            "zh": "安德鲁·休伯曼、勒布朗·詹姆斯、彼得·阿蒂亚",
        },
        "category": {
            "ko": "신체/에너지",
            "en": "Body & Energy",
            "ja": "身体/エネルギー",
            "zh": "身体与能量",
        },
        "sheet_domain": {
            "ko": "⚡ 신체 & 에너지",
            "en": "⚡ Body & Energy",
            "ja": "⚡ 身体＆エネルギー",
            "zh": "⚡ 身体与能量",
        },
    },
    3: {
        "code": "L3",
        "gurus": {
            "ko": "마르쿠스 아우렐리우스, 레이 달리오, 세네카",
            "en": "Marcus Aurelius, Ray Dalio, Viktor Frankl",
            "ja": "マルクス・アウレリウス、レイ・ダリオ、V・フランクル",
            "zh": "马可·奥勒留、瑞·达利欧、维克多·弗兰克尔",
        },
        "category": {
            "ko": "멘탈/마인드셋",
            "en": "Mental & Mindset",
            "ja": "メンタル/思考法",
            "zh": "心理与思维",
        },
        "sheet_domain": {
            "ko": "🧠 멘탈 & 마인드셋",
            "en": "🧠 Mental & Mindset",
            "ja": "🧠 メンタル＆思考",
            "zh": "🧠 心理与思维",
        },
    },
    4: {
        "code": "L4",
        "gurus": {
            "ko": "무라카미 하루키, 빌 게이츠, 리처드 파인만",
            "en": "Haruki Murakami, Bill Gates, Richard Feynman",
            "ja": "村上春樹、ビル・ゲイツ、R・ファインマン",
            "zh": "村上春树、比尔·盖茨、理查德·费曼",
        },
        "category": {
            "ko": "창의/학습",
            "en": "Creativity & Learning",
            "ja": "創造/学習",
            "zh": "创造与学习",
        },
        "sheet_domain": {
            "ko": "📚 창의성 & 지적성장",
            "en": "📚 Creativity & Learning",
            "ja": "📚 創造性＆知的成長",
            "zh": "📚 创造力与认知成长",
        },
    },
    5: {
        "code": "L5",
        "gurus": {
            "ko": "데일 카네기, 제프 베조스, 찰리 멍거",
            "en": "Dale Carnegie, Jeff Bezos, Charlie Munger",
            "ja": "D・カーネギー、ジェフ・ベゾス、チャーリー・マンガー",
            "zh": "戴尔·卡内基、杰夫·贝索斯、查理·芒格",
        },
        "category": {
            "ko": "관계/리더십",
            "en": "Leadership & Empathy",
            "ja": "人間関係/リーダー",
            "zh": "人际与领导力",
        },
        "sheet_domain": {
            "ko": "🤝 관계 & 리더십",
            "en": "🤝 Relationships & Leadership",
            "ja": "🤝 人間関係＆リーダー",
            "zh": "🤝 人际关系与领导力",
        },
    },
    6: {
        "code": "L6",
        "gurus": {
            "ko": "모건 하우절, 워런 버핏",
            "en": "Morgan Housel, Warren Buffett, Charlie Munger",
            "ja": "モーガン・ハウセル、W・バフェット",
            "zh": "摩根·豪泽尔、沃伦·巴菲特",
        },
        "category": {
            "ko": "자산/재무",
            "en": "Wealth & Finance",
            "ja": "資産/財務",
            "zh": "财富与理财",
        },
        "sheet_domain": {
            "ko": "💰 재정 & 자산관리",
            "en": "💰 Wealth & Finance",
            "ja": "💰 財務＆資産管理",
            "zh": "💰 财务与资产管理",
        },
    },
    7: {
        "code": "L7",
        "gurus": {
            "ko": "제임스 클리어, 벤자민 프랭클린",
            "en": "James Clear, Benjamin Franklin, Tim Ferriss",
            "ja": "ジェームズ・クリアー、B・フランクリン",
            "zh": "詹姆斯·克利尔、本杰明·富兰克林",
        },
        "category": {
            "ko": "시스템/루틴",
            "en": "Systems & Routines",
            "ja": "システム/習慣化",
            "zh": "系统与日常",
        },
        "sheet_domain": {
            "ko": "⚙️ 시스템 & 루틴",
            "en": "⚙️ Systems & Routines",
            "ja": "⚙️ システム＆習慣",
            "zh": "⚙️ 系统与习惯",
        },
    },
}

RAW_HABITS = [
    # --- Domain 1: Business & Productivity (1..5) ---
    {
        "id": 1, "domain": 1, "difficulty": "⭐⭐⭐",
        "role": {"ko": "워런 버핏", "en": "Warren Buffett", "ja": "ウォーレン・バフェット", "zh": "沃伦·巴菲特"},
        "name": {
            "ko": "워런 버핏의 5/25 우선순위",
            "en": "Warren Buffett's 5/25 Priority Rule",
            "ja": "バフェットの5/25優先順位ルール",
            "zh": "巴菲特的5/25优先级法则",
        },
        "excel_name": {
            "ko": "5/25 우선순위 법칙",
            "en": "5/25 Priority Law",
            "ja": "5/25優先順位の法則",
            "zh": "5/25 优先级法则",
        },
        "philosophy": {
            "ko": "생산성의 본질은 '무엇을 할까'가 아니라 '무엇을 하지 않을까'를 결정하는 것",
            "en": "Productivity is less about what you do than what you deliberately avoid.",
            "ja": "生産性の本質は『何をするか』ではなく『何をしないか』を決めること。",
            "zh": "效率的本质不在于“做什么”，而在于决定“不做什么”。",
        },
        "protocol": {
            "ko": "목표 25개를 적고, 가장 중요한 5개만 동그라미 친 뒤 나머지 20개는 절대 피해야 할 리스트로 규정",
            "en": "List 25 goals, circle the vital Top 5, and put the remaining 20 on your Avoid-At-All-Cost list.",
            "ja": "目標を25個書き出し上位5個だけに集中し、残り20個は絶対やらないリストに入れる。",
            "zh": "写下25个目标，圈出最核心的5个，把其余20个列入绝对避免清单。",
        },
        "freq": {"ko": "일일/주간", "en": "Daily/Weekly", "ja": "毎日/週次", "zh": "每日/每周"},
        "keywords": {
            "ko": ["우선순위", "5/25", "버핏", "핵심과제", "가장 중요한", "우선순위선정"],
            "en": ["priority", "5/25", "buffett", "top 5", "top priority", "prioritize"],
            "ja": ["優先順位", "バフェット", "最優先", "重要課題", "5/25"],
            "zh": ["优先级", "巴菲特", "核心任务", "最重要", "5/25"],
        },
    },
    {
        "id": 2, "domain": 1, "difficulty": "⭐⭐⭐⭐",
        "role": {"ko": "캘 뉴포트", "en": "Cal Newport", "ja": "カル・ニューポート", "zh": "卡尔·纽波特"},
        "name": {
            "ko": "캘 뉴포트의 90분 무중단 딥워크",
            "en": "Cal Newport's 90-Min Deep Work Block",
            "ja": "ニューポートの90分ディープワーク",
            "zh": "卡尔·纽波特的90分钟深度工作",
        },
        "excel_name": {
            "ko": "무중단 90분 딥워크 블록",
            "en": "90-Min Distraction-Free Deep Work",
            "ja": "中断なし90分ディープワーク",
            "zh": "90分钟无干扰深度工作模块",
        },
        "philosophy": {
            "ko": "인지적 한계를 넘어서는 고도의 집중력이야말로 AI 시대의 최고 경쟁력",
            "en": "Focused cognition without distraction is the rarest superpower in the AI era.",
            "ja": "気を散らさずに深く集中する能力こそがAI時代の最大の競争力。",
            "zh": "超越认知极限的深度专注力，正是AI时代最稀缺的竞争力。",
        },
        "protocol": {
            "ko": "오전 중 90분 동안 스마트폰 전원을 끄고 단 하나의 고난도 프로젝트에만 몰입",
            "en": "Turn off phone notifications and focus 90 minutes uninterrupted on a single high-value task.",
            "ja": "午前中に90分間スマホを切り、最も難度の高い1つの課題に完全集中する。",
            "zh": "上午关闭手机干扰，连续90分钟全神贯注攻克单一高价值项目。",
        },
        "freq": {"ko": "매일(평일)", "en": "Weekdays", "ja": "毎日(平日)", "zh": "每个工作日"},
        "keywords": {
            "ko": ["딥워크", "몰입", "집중", "스마트폰끄기", "90분", "비행기모드"],
            "en": ["deep work", "deepwork", "90m", "90 min", "airplane mode", "focus block"],
            "ja": ["ディープワーク", "深い集中", "90分集中", "機内モード", "没頭"],
            "zh": ["深度工作", "专注90", "飞行模式", "心流", "沉浸工作"],
        },
    },
    {
        "id": 3, "domain": 1, "difficulty": "⭐⭐⭐",
        "role": {"ko": "피터 드러커", "en": "Peter Drucker", "ja": "ピーター・ドラッカー", "zh": "彼得·德鲁克"},
        "name": {
            "ko": "피터 드러커의 시간 가계부 기록",
            "en": "Peter Drucker's Time Audit Ledger",
            "ja": "ドラッカーの時間家計簿記録",
            "zh": "彼得·德鲁克的时间账本记录",
        },
        "excel_name": {
            "ko": "시간 가계부 기록 (Time Tracking)",
            "en": "Time Tracking & Audit",
            "ja": "時間家計簿 (タイムログ)",
            "zh": "时间账本追踪记录",
        },
        "philosophy": {
            "ko": "시간을 측정하지 못하면 결코 관리할 수 없다",
            "en": "You cannot manage your time until you actually know where it goes.",
            "ja": "測定できないものは管理できない。時間の使い方を記録することから始まる。",
            "zh": "无法衡量时间，就永远无法管理时间。",
        },
        "protocol": {
            "ko": "매일 자신의 15분~30분 단위 시간 사용 내역을 기록하여 새는 시간 30% 즉시 차단",
            "en": "Log your time in 15-30 minute blocks daily to cut 30% of hidden time leaks.",
            "ja": "毎日15〜30分単位で時間の使途を記録し、浪費される時間を可視化する。",
            "zh": "每天按15~30分钟颗粒度记录时间去向，立即堵住30%时间漏洞。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["시간가계부", "시간기록", "시간추적", "드러커", "시간관리"],
            "en": ["time log", "time tracking", "time audit", "drucker", "logged time"],
            "ja": ["時間家計簿", "タイムログ", "時間記録", "ドラッカー", "時間追跡"],
            "zh": ["时间账本", "时间记录", "时间追踪", "德鲁克", "时间审计"],
        },
    },
    {
        "id": 4, "domain": 1, "difficulty": "⭐⭐⭐⭐⭐",
        "role": {"ko": "일론 머스크", "en": "Elon Musk", "ja": "イーロン・マスク", "zh": "埃隆·马斯克"},
        "name": {
            "ko": "일론 머스크의 5분 타임박싱 & 제1원칙",
            "en": "Elon Musk's Timeboxing & First Principles",
            "ja": "マスクのタイムボクシング＆第一原理",
            "zh": "马斯克的5分钟时间盒与第一性原理",
        },
        "excel_name": {
            "ko": "5분 타임박싱 & 제1원칙 사고",
            "en": "5-Min Timeboxing & First Principles",
            "ja": "5分タイムボックス＆第一原理思考",
            "zh": "5分钟时间盒与第一性原理思考",
        },
        "philosophy": {
            "ko": "물리학적 관점에서 기본 진실로 분해하고 시간을 잘게 쪼개어 지연을 방지",
            "en": "Boil problems down to fundamental truths and schedule tight calendar blocks.",
            "ja": "問題を本質的な真実まで分解し、予定を細かく区切って遅延を防ぐ。",
            "zh": "从物理学基本事实出发拆解问题，切分紧致的时间块消除拖延。",
        },
        "protocol": {
            "ko": "캘린더를 5~15분 단위 블록으로 스케줄링하고 기존 관행 대신 본질부터 질문",
            "en": "Schedule the day in tight 5-15m timeboxes and question every inherited assumption.",
            "ja": "カレンダーを5〜15分単位のブロックで区切り、慣例ではなく本質から問い直す。",
            "zh": "用5~15分钟时间盒排满日程，不盲从惯例而从本质重新提问。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["타임박싱", "머스크", "스케줄링", "제1원칙", "시간블록"],
            "en": ["timebox", "timeboxing", "first principles", "elon", "time block"],
            "ja": ["タイムボックス", "第一原理", "時間ブロック", "イーロン"],
            "zh": ["时间盒", "第一性原理", "马斯克", "时间块", "排期"],
        },
    },
    {
        "id": 5, "domain": 1, "difficulty": "⭐⭐",
        "role": {"ko": "제프 베조스", "en": "Jeff Bezos", "ja": "ジェフ・ベゾス", "zh": "杰夫·贝索斯"},
        "name": {
            "ko": "제프 베조스의 오전 고부가가치 의사결정",
            "en": "Jeff Bezos's Morning High-IQ Decisions",
            "ja": "ベゾスの午前高価値意思決定",
            "zh": "贝索斯的上午高价值决策习惯",
        },
        "excel_name": {
            "ko": "오전 고부가가치 의사결정",
            "en": "Morning High-Value Decisions",
            "ja": "午前の高付加価値意思決定",
            "zh": "上午高价值战略决策",
        },
        "philosophy": {
            "ko": "하루에 최고 품질의 의사결정 3개만 제대로 내리면 리더로서 충분하다",
            "en": "Making three high-quality decisions before noon beats twelve exhausted choices later.",
            "ja": "1日に3つの質の高い意思決定ができればリーダーとして十分である。",
            "zh": "每天上午只需做出三个高质量的关键决策，就已胜过盲目忙碌。",
        },
        "protocol": {
            "ko": "정신이 가장 맑은 오전 10시~12시에 가장 중요한 회의와 전략적 판단 배치",
            "en": "Place strategic thinking and key decisions during peak 10 AM - 12 PM clarity.",
            "ja": "思考が最も冴える午前10〜12時に最重要の会議・戦略判断を配置する。",
            "zh": "在头脑最清醒的上午10~12点安排最核心的战略决策与讨论。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["베조스", "오전회의", "의사결정", "전략판단", "핵심결정"],
            "en": ["bezos", "high value decision", "morning decision", "strategic decision", "key decision"],
            "ja": ["ベゾス", "意思決定", "午前会議", "戦略判断"],
            "zh": ["贝索斯", "高价值决策", "上午决策", "战略判断", "关键决定"],
        },
    },
    # --- Domain 2: Body & Energy (6..10) ---
    {
        "id": 6, "domain": 2, "difficulty": "⭐⭐",
        "role": {"ko": "앤드루 후버만", "en": "Andrew Huberman", "ja": "A・フーバーマン", "zh": "安德鲁·休伯曼"},
        "name": {
            "ko": "앤드루 후버만의 아침 자연광 15분 노출",
            "en": "Huberman's 15-Min Morning Sunlight",
            "ja": "フーバーマンの朝自然光15分浴び",
            "zh": "休伯曼的清晨自然光照15分钟",
        },
        "excel_name": {
            "ko": "기상 직후 자연광 15분 노출",
            "en": "15-Min Morning Outdoor Sunlight",
            "ja": "起床直後の自然光15分露出",
            "zh": "起床后15分钟自然光照",
        },
        "philosophy": {
            "ko": "망막 세포를 통한 빛 자극이 24시간 일주기 리듬과 코르티솔 분비를 리셋",
            "en": "Morning photons reset your circadian pacemaker and anchor healthy cortisol & melatonin timing.",
            "ja": "起床後の太陽光刺激が体内時計とコルチゾール・メラトニンの分泌リズムを整える。",
            "zh": "清晨自然光刺激视网膜神经节细胞，重置昼夜节律与皮质醇峰值。",
        },
        "protocol": {
            "ko": "기상 후 30분 이내에 야외로 나가 선글라스 없이 자연 햇빛을 10~15분간 직시",
            "en": "Step outside within 30 minutes of waking for 10-15 minutes of daylight without sunglasses.",
            "ja": "起床後30分以内に外へ出てサングラスなしで自然光を10〜15分浴びる。",
            "zh": "醒后30分钟内到户外，不戴墨镜感受10~15分钟自然日光。",
        },
        "freq": {"ko": "매일(아침)", "en": "Daily (AM)", "ja": "毎朝", "zh": "每日早晨"},
        "keywords": {
            "ko": ["햇빛", "햇볕", "자연광", "일조", "아침산책", "후버만", "눈부심"],
            "en": ["sunlight", "morning sun", "daylight", "outdoor light", "huberman", "morning walk"],
            "ja": ["日光", "朝日", "自然光", "朝散歩", "フーバーマン", "太陽"],
            "zh": ["阳光", "晒太阳", "自然光", "晨走", "休伯曼", "日照"],
        },
    },
    {
        "id": 7, "domain": 2, "difficulty": "⭐⭐⭐",
        "role": {"ko": "후버만 / 조 로건", "en": "Huberman / Joe Rogan", "ja": "フーバーマン/ローガン", "zh": "休伯曼 / 乔·罗根"},
        "name": {
            "ko": "후버만/조로건의 찬물 샤워 & 도파민 리셋",
            "en": "Cold Shower / Plunge Dopamine Reset",
            "ja": "冷水シャワー＆ドーパミンリセット",
            "zh": "冷水澡 / 冰浴多巴胺重置",
        },
        "excel_name": {
            "ko": "찬물 샤워 / 냉수욕 도파민 리셋",
            "en": "Cold Exposure Dopamine Reset",
            "ja": "冷水シャワー/冷却リセット",
            "zh": "冷水澡多巴胺重塑",
        },
        "philosophy": {
            "ko": "신체적 스트레스 유발을 통해 지속적인 도파민 기준선 250% 상승 및 항염 효과",
            "en": "Deliberate cold exposure triggers sustained dopamine elevation, alertness, and stress resilience.",
            "ja": "意図的な寒冷刺激によりドーパミン基準値を持続的に高め、回復力と覚醒度を引き上げる。",
            "zh": "可控的冷水刺激可持久提升多巴胺基线与精力警觉度。",
        },
        "protocol": {
            "ko": "샤워 마지막 1~2분을 차가운 물로 마무리하여 교감신경 각성 및 회복력 증진",
            "en": "Finish your shower with 1-2 minutes of cold water to activate resilience and focus.",
            "ja": "シャワーの最後1〜2分を冷水に切り替え、交感神経を適度に刺激して覚醒させる。",
            "zh": "淋浴最后1~2分钟使用冷水，激发清醒专注与恢复力。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["찬물샤워", "냉수욕", "도파민", "찬물", "샤워마무리", "냉수"],
            "en": ["cold shower", "cold plunge", "ice bath", "cold exposure", "cold water"],
            "ja": ["冷水シャワー", "冷水浴", "水風呂", "アイスバス", "冷たいシャワー"],
            "zh": ["冷水澡", "洗冷水", "冰浴", "冷浴", "冷水淋浴"],
        },
    },
    {
        "id": 8, "domain": 2, "difficulty": "⭐⭐⭐",
        "role": {"ko": "매튜 워커", "en": "Matthew Walker", "ja": "マシュー・ウォーカー", "zh": "马修·沃克"},
        "name": {
            "ko": "매튜 워커의 취침 1시간 전 디지털 디톡스",
            "en": "Matthew Walker's Pre-Bed Digital Detox",
            "ja": "ウォーカーの就寝1時間前デジタル断ち",
            "zh": "马修·沃克的睡前1小时数字排毒",
        },
        "excel_name": {
            "ko": "취침 1시간 전 디지털 디톡스",
            "en": "Pre-Sleep Digital Detox (1h)",
            "ja": "就寝1時間前デジタルデトックス",
            "zh": "睡前1小时数字排毒",
        },
        "philosophy": {
            "ko": "블루라이트는 멜라토닌 분비를 2시간 지연시켜 수면의 질을 치명적으로 저하",
            "en": "Evening screens suppress melatonin release and fragment restorative deep & REM sleep.",
            "ja": "夜のブルーライトはメラトニン分泌を遅らせ、深い睡眠を著しく損なう。",
            "zh": "睡前蓝光会延迟褪黑素分泌并破坏深度睡眠与REM睡眠。",
        },
        "protocol": {
            "ko": "취침 60분 전 스마트폰, PC 등 화면을 끄고 침실 조명을 어둡게 세팅",
            "en": "Put away phones and screens 60 minutes before bed and dim bedroom lighting.",
            "ja": "就寝60分前にスマホやPC画面を閉じ、部屋の照明を暗く落ち着かせる。",
            "zh": "睡前60分钟关闭手机电脑屏幕，调暗卧室灯光。",
        },
        "freq": {"ko": "매일(저녁)", "en": "Daily (PM)", "ja": "毎晩", "zh": "每晚"},
        "keywords": {
            "ko": ["디지털디톡스", "스마트폰끄기", "화면끄기", "취침전", "블루라이트", "폰치우기"],
            "en": ["digital detox", "screens off", "no phone before bed", "blue light", "screen off"],
            "ja": ["デジタルデトックス", "スマホ見ない", "ブルーライト", "画面オフ", "寝る前スマホ"],
            "zh": ["数字排毒", "关屏幕", "不用手机", "睡前远离手机", "防蓝光"],
        },
    },
    {
        "id": 9, "domain": 2, "difficulty": "⭐⭐⭐",
        "role": {"ko": "르브론 제임스", "en": "LeBron James", "ja": "レブロン・ジェームズ", "zh": "勒布朗·詹姆斯"},
        "name": {
            "ko": "르브론 제임스의 8시간 완전 수면 환경",
            "en": "LeBron James's 8-Hr Deep Sleep Setup",
            "ja": "レブロンの8時間完全睡眠環境",
            "zh": "勒布朗·詹姆斯的8小时优质睡眠",
        },
        "excel_name": {
            "ko": "8~9시간 완전 수면 환경 구축",
            "en": "8-Hour Dark & Cool Sleep Hygiene",
            "ja": "8時間完全睡眠・暗室環境",
            "zh": "8小时全黑凉爽深睡环境",
        },
        "philosophy": {
            "ko": "신체 및 뇌 조직의 완벽한 재생은 오직 깊은 수면(REM/비REM)에서만 발생",
            "en": "Physical and cognitive repair happens only during uninterrupted deep & REM sleep.",
            "ja": "身体と脳の完全な修復は、深く質の高い睡眠中にのみ行われる。",
            "zh": "身体与大脑的深度修复只能在充沛完整的睡眠周期中实现。",
        },
        "protocol": {
            "ko": "침실 온도 19~20도 유지, 암막 커튼으로 빛 100% 차단, 매일 동일 시간 기상",
            "en": "Keep the room cool (19-20°C / 67°F), pitch black, and wake at a consistent hour.",
            "ja": "寝室を19〜20℃・完全遮光に保ち、毎日決まった時刻に起床する。",
            "zh": "保持卧室凉爽（19~20度）、完全遮光，并固定每天起床时间。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["수면", "8시간", "암막커튼", "숙면", "잠자기", "취침", "르브론"],
            "en": ["8 hours sleep", "8h sleep", "good sleep", "deep sleep", "blackout curtain", "lebron"],
            "ja": ["8時間睡眠", "熟睡", "快眠", "遮光カーテン", "レブロン"],
            "zh": ["8小时睡眠", "深睡", "优质睡眠", "遮光窗帘", "勒布朗"],
        },
    },
    {
        "id": 10, "domain": 2, "difficulty": "⭐⭐⭐",
        "role": {"ko": "피터 아티아", "en": "Peter Attia", "ja": "ピーター・アティア", "zh": "彼得·阿蒂亚"},
        "name": {
            "ko": "피터 아티아의 주 150분 Zone 2 유산소",
            "en": "Peter Attia's Zone 2 Cardio (150m/wk)",
            "ja": "アティアの週150分Zone 2有酸素",
            "zh": "彼得·阿蒂亚的每周150分钟Zone2有氧",
        },
        "excel_name": {
            "ko": "주 150분 Zone 2 심폐 유산소",
            "en": "150m/wk Zone 2 Aerobic Base",
            "ja": "週150分 Zone2 有酸素運動",
            "zh": "每周150分钟 Zone 2 心肺有氧",
        },
        "philosophy": {
            "ko": "미토콘드리아 건강과 대사 유연성은 100세 건강수명의 핵심 지표",
            "en": "Mitochondrial density and metabolic flexibility are pillars of healthspan.",
            "ja": "ミトコンドリア機能と代謝柔軟性は健康寿命を伸ばす最重要指標。",
            "zh": "线粒体密度与代谢灵活性是延展健康寿命的核心支柱。",
        },
        "protocol": {
            "ko": "코로 호흡하며 대화가 겨우 가능한 강도의 걷기/자전거를 주 3~4회 40분씩 실천",
            "en": "Do 40m brisk walking, cycling, or jogging at nasal-breathing pace 3-4x weekly.",
            "ja": "鼻呼吸で会話が続けられる強度（ウォーキング・自転車・ジョグ）を週3〜4回実施。",
            "zh": "保持可鼻呼吸交谈的中等强度快走、骑行或慢跑，每次40分钟。",
        },
        "freq": {"ko": "주 3~4회", "en": "3-4x / Week", "ja": "週3〜4回", "zh": "每周3~4次"},
        "keywords": {
            "ko": ["유산소", "zone2", "존2", "러닝", "달리기", "자전거", "가벼운운동", "걷기"],
            "en": ["zone 2", "zone2", "cardio", "running", "jogging", "cycling", "brisk walk"],
            "ja": ["有酸素", "zone2", "ランニング", "ジョギング", "ウォーキング", "サイクリング"],
            "zh": ["有氧", "zone2", "慢跑", "跑步", "骑行", "快走"],
        },
    },
    # --- Domain 3: Mental & Mindset (11..15) ---
    {
        "id": 11, "domain": 3, "difficulty": "⭐⭐",
        "role": {"ko": "마르쿠스 아우렐리우스", "en": "Marcus Aurelius", "ja": "マルクス・アウレリウス", "zh": "马可·奥勒留"},
        "name": {
            "ko": "마르쿠스 아우렐리우스의 스토아 통제의 이분법",
            "en": "Marcus Aurelius's Dichotomy of Control",
            "ja": "ストア派『制御の二分法』実践",
            "zh": "马可·奥勒留的斯多葛控制二分法",
        },
        "excel_name": {
            "ko": "스토아적 통제의 이분법",
            "en": "Stoic Dichotomy of Control",
            "ja": "ストア的制御の二分法",
            "zh": "斯多葛控制二分法",
        },
        "philosophy": {
            "ko": "우리가 통제할 수 있는 것은 우리의 생각과 태도뿐, 외부 사건은 통제할 수 없다",
            "en": "You have power over your mind—not outside events. Realize this, and find strength.",
            "ja": "我々が支配できるのは自らの思考と態度のみであり、外の出来事は支配できない。",
            "zh": "你能掌控的唯有自己的心念与态度，而非外界风云。",
        },
        "protocol": {
            "ko": "매일 아침 불안한 감정이 들 때 '내가 통제할 수 있는가? 없는가?'를 종이에 분류",
            "en": "Separate worries on paper into 'In My Control' vs 'Outside My Control' each morning.",
            "ja": "不安を感じたら『自分で制御できること/できないこと』を紙に仕分ける。",
            "zh": "面对焦虑时在纸上划分“我能掌控的”与“无法掌控的”，只关注前者。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["통제의이분법", "스토아", "아우렐리우스", "걱정비우기", "통제불가능", "내면평정"],
            "en": ["stoic", "aurelius", "dichotomy of control", "in my control", "inner peace"],
            "ja": ["ストア", "制御の二分法", "アウレリウス", "内面の静穏"],
            "zh": ["斯多葛", "控制二分法", "奥勒留", "内心平静", "放下焦虑"],
        },
    },
    {
        "id": 12, "domain": 3, "difficulty": "⭐⭐⭐",
        "role": {"ko": "레이 달리오", "en": "Ray Dalio", "ja": "レイ・ダリオ", "zh": "瑞·达利欧"},
        "name": {
            "ko": "레이 달리오의 초월명상 20분",
            "en": "Ray Dalio's 20-Min Meditation",
            "ja": "レイ・ダリオの超越瞑想20分",
            "zh": "瑞·达利欧的20分钟超越冥想",
        },
        "excel_name": {
            "ko": "초월명상(TM) 20분",
            "en": "20-Min Daily Meditation",
            "ja": "超越瞑想(TM) 20分",
            "zh": "每日20分钟超越冥想",
        },
        "philosophy": {
            "ko": "마음의 고요와 직관을 회복하여 시장의 변동성과 감정적 충동을 다스림",
            "en": "Equanimity and clear intuition unlock wise action amid chaos.",
            "ja": "心の静けさと直感を取り戻し、感情的な衝動に振り回されない視座を養う。",
            "zh": "恢复内心的宁静与直觉洞察，在动荡中保持冷静。",
        },
        "protocol": {
            "ko": "아침 업무 시작 전 조용한 공간에서 눈을 감고 20분간 명상 수행",
            "en": "Sit quietly with eyes closed for 20 minutes of focused breath/mindfulness meditation.",
            "ja": "朝の業務前など静かな場所で目を閉じ、20分間の瞑想を行う。",
            "zh": "工作开始前在安静处闭目冥想20分钟。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["명상", "초월명상", "호흡명상", "달리오", "마인드풀니스", "20분명상"],
            "en": ["meditation", "meditate", "mindfulness", "20m meditation", "breathwork"],
            "ja": ["瞑想", "マインドフルネス", "超越瞑想", "呼吸瞑想"],
            "zh": ["冥想", "静坐", "正念", "呼吸冥想", "超越冥想"],
        },
    },
    {
        "id": 13, "domain": 3, "difficulty": "⭐⭐⭐",
        "role": {"ko": "팀 페리스", "en": "Tim Ferriss", "ja": "ティム・フェリス", "zh": "蒂姆·费里斯"},
        "name": {
            "ko": "팀 페리스의 두려움 설정 (Fear Setting)",
            "en": "Tim Ferriss's Fear-Setting Exercise",
            "ja": "ティム・フェリスのフィア・セッティング",
            "zh": "蒂姆·费里斯的恐惧设定练习",
        },
        "excel_name": {
            "ko": "두려움 설정 (Fear Setting)",
            "en": "Fear Setting Protocol",
            "ja": "恐怖設定 (フィア・セッティング)",
            "zh": "恐惧设定 (Fear Setting)",
        },
        "philosophy": {
            "ko": "행동하지 못하는 이유는 막연한 두려움 때문이며, 최악을 정의하면 자유로워진다",
            "en": "Vague fear paralyzes action; naming the worst case sets you free to act.",
            "ja": "行動できない原因は漠然とした恐怖にあり、最悪を明確化すれば自由になれる。",
            "zh": "让人停滞的往往是模糊的恐惧；明确最坏结果就能重获行动力。",
        },
        "protocol": {
            "ko": "시도하기 두려운 일의 '최악의 결과', '예방법', '복구법'을 상세히 적어보기",
            "en": "Write out three columns for scary decisions: Define worst case, Prevent, and Repair.",
            "ja": "躊躇している挑戦について『最悪の結果・予防策・回復策』を書き出す。",
            "zh": "写出不敢尝试之事的“最坏结果、预防措施、补救方法”。",
        },
        "freq": {"ko": "주간/월간", "en": "Weekly/Monthly", "ja": "週次/月次", "zh": "每周/每月"},
        "keywords": {
            "ko": ["두려움설정", "최악시나리오", "불안정의", "팀페리스", "극복"],
            "en": ["fear setting", "fear-setting", "worst case", "define fear", "tim ferriss"],
            "ja": ["恐怖設定", "フィアセッティング", "最悪のシナリオ", "不安を定義"],
            "zh": ["恐惧设定", "最坏情况", "直面恐惧", "蒂姆费里斯"],
        },
    },
    {
        "id": 14, "domain": 3, "difficulty": "⭐⭐⭐⭐",
        "role": {"ko": "빅터 프랭클", "en": "Viktor Frankl", "ja": "ヴィクトール・フランクル", "zh": "维克多·弗兰克尔"},
        "name": {
            "ko": "빅터 프랭클의 자극과 반응 사이 공간 확보",
            "en": "Frankl's Pause Between Stimulus & Response",
            "ja": "フランクル『刺激と反応の間の余白』",
            "zh": "弗兰克尔的刺激与回应间的停顿",
        },
        "excel_name": {
            "ko": "자극과 반응 사이의 공간 확보",
            "en": "10-Sec Pause Before Reacting",
            "ja": "刺激と反応の間に10秒の余白",
            "zh": "刺激与反应间留出10秒空间",
        },
        "philosophy": {
            "ko": "자극과 반응 사이에는 선택할 수 있는 자유와 공간이 존재한다",
            "en": "Between stimulus and response there is a space where our freedom to choose resides.",
            "ja": "刺激と反応の間にはスペースがあり、そこに人間の選択の自由が存在する。",
            "zh": "在刺激与回应之间存在一段空间，那里蕴含着我们的选择自由。",
        },
        "protocol": {
            "ko": "분노나 충동이 올라올 때 즉각 반응하지 않고 10초간 깊은 호흡으로 멈추기",
            "en": "Take a 10-second deep breath before replying when anger or impulse flares.",
            "ja": "怒りや衝動を感じたとき即座に反応せず、10秒間の深呼吸で間を作る。",
            "zh": "情绪冲动涌来时先深呼吸停顿10秒，然后再选择如何回应。",
        },
        "freq": {"ko": "매일 수시", "en": "As Needed", "ja": "毎日随時", "zh": "每日随时"},
        "keywords": {
            "ko": ["10초멈춤", "화참기", "감정조절", "분노조절", "반응선택", "심호흡"],
            "en": ["10 second pause", "deep breath", "emotional regulation", "frankl", "pause before reacting"],
            "ja": ["10秒ストップ", "感情コントロール", "深呼吸", "フランクル", "一呼吸"],
            "zh": ["停顿10秒", "情绪调节", "控制脾气", "深呼吸冷静", "弗兰克尔"],
        },
    },
    {
        "id": 15, "domain": 3, "difficulty": "⭐",
        "role": {"ko": "오프라 윈프리", "en": "Oprah Winfrey", "ja": "オプラ・ウィンフリー", "zh": "奥普拉·温弗瑞"},
        "name": {
            "ko": "오프라 윈프리의 매일 5가지 감사일기",
            "en": "Oprah Winfrey's 5 Gratitude Journal",
            "ja": "オプラの毎日5つの感謝日記",
            "zh": "奥普拉的每日5件感恩日记",
        },
        "excel_name": {
            "ko": "매일 5가지 감사 일기 (Gratitude)",
            "en": "Daily 5-Item Gratitude Journal",
            "ja": "毎日5つの感謝ジャーナル",
            "zh": "每日五件感恩日记",
        },
        "philosophy": {
            "ko": "가진 것에 집중할 때 마음의 결핍이 사라지고 긍정적 기회가 확장된다",
            "en": "Focusing on what you have dissolves scarcity and expands emotional resilience.",
            "ja": "持っているものに目を向けることで欠乏感が消え、前向きな機会が広がる。",
            "zh": "聚焦已拥有之物，匮乏感消退，幸福感与复原力随之扩大。",
        },
        "protocol": {
            "ko": "잠들기 전 오늘 하루 진심으로 감사했던 사소한 일 5가지를 기록",
            "en": "Write down 5 specific things you felt genuinely grateful for before sleep.",
            "ja": "就寝前に、今日心から感謝できたささやかな出来事を5つ書き留める。",
            "zh": "睡前写下今天真诚感到感恩的5件小事。",
        },
        "freq": {"ko": "매일(저녁)", "en": "Daily (PM)", "ja": "毎晩", "zh": "每晚"},
        "keywords": {
            "ko": ["감사일기", "감사", "오프라", "고마움", "긍정일기"],
            "en": ["gratitude", "grateful", "thankful journal", "oprah", "5 things grateful"],
            "ja": ["感謝日記", "感謝ジャーナル", "オプラ", "感謝リスト"],
            "zh": ["感恩日记", "感恩清单", "感恩", "奥普拉", "正向日记"],
        },
    },
    # --- Domain 4: Creativity & Learning (16..20) ---
    {
        "id": 16, "domain": 4, "difficulty": "⭐⭐⭐⭐⭐",
        "role": {"ko": "무라카미 하루키", "en": "Haruki Murakami", "ja": "村上春樹", "zh": "村上春树"},
        "name": {
            "ko": "무라카미 하루키의 새벽 기상 & 집필 루틴",
            "en": "Haruki Murakami's Dawn Writing Routine",
            "ja": "村上春樹の早朝起床＆執筆ルーティン",
            "zh": "村上春树的清晨早起写作习惯",
        },
        "excel_name": {
            "ko": "새벽 4시 기상 & 매일 10매 집필",
            "en": "Early Wakeup & Daily Writing Ritual",
            "ja": "早朝起床＆毎日原稿用紙10枚執筆",
            "zh": "早起与每日定时定量写作",
        },
        "philosophy": {
            "ko": "영감을 기다리지 않고 육체적 규율을 통해 창작의 신전을 짓는다",
            "en": "Repetition and physical discipline invite inspiration rather than waiting for moods.",
            "ja": "インスピレーションを待たず、日々の規律と反復によって創造の場を維持する。",
            "zh": "不坐等灵感降临，而是用铁律般的日常节奏召唤创造力。",
        },
        "protocol": {
            "ko": "매일 같은 시간 책상에 앉아 분량을 채우고, 이후 10km 달리기 병행",
            "en": "Sit at your desk at a fixed early hour to produce your daily word quota, then exercise.",
            "ja": "毎日決まった早朝に机に向かい一定の分量を書き切り、その後運動を行う。",
            "zh": "每天固定清晨时间坐到书桌前完成定量写作，随后坚持跑步锻炼。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["새벽기상", "글쓰기", "집필", "하루키", "원고", "원고지", "창작"],
            "en": ["early wakeup", "morning pages", "daily writing", "murakami", "wrote draft"],
            "ja": ["早朝起床", "執筆", "原稿", "村上春樹", "創作ルーティン"],
            "zh": ["早起写作", "写作", "写稿", "村上春树", "创作习惯"],
        },
    },
    {
        "id": 17, "domain": 4, "difficulty": "⭐⭐⭐",
        "role": {"ko": "빌 게이츠", "en": "Bill Gates", "ja": "ビル・ゲイツ", "zh": "比尔·盖茨"},
        "name": {
            "ko": "빌 게이츠의 하루 1시간 독서 루틴",
            "en": "Bill Gates's 1-Hour Daily Reading",
            "ja": "ビル・ゲイツの1日1時間読書",
            "zh": "比尔·盖茨的每日1小时阅读",
        },
        "excel_name": {
            "ko": "하루 1시간 독서 & Think Week",
            "en": "1-Hour Focused Reading & Think Week",
            "ja": "1日1時間読書 ＆ Think Week",
            "zh": "每日1小时深度阅读与思考周",
        },
        "philosophy": {
            "ko": "깊이 있는 독서만이 단편적인 정보 더미 속에서 통찰의 맥락을 형성한다",
            "en": "Deep reading stitches fragmented facts into enduring mental models.",
            "ja": "深い読書だけが断片的な情報の山から本質的な洞察の文脈を紡ぎ出す。",
            "zh": "唯有沉浸式深度阅读，才能将碎片信息编织成洞察脉络。",
        },
        "protocol": {
            "ko": "주말/매일 최소 1시간 전자기기 없이 책 한 권 집중 정독",
            "en": "Read a physical or distraction-free book for at least 30-60 minutes daily.",
            "ja": "電子機器から離れ、1日30〜60分以上じっくり本を読み込む。",
            "zh": "每天至少远离屏幕静心精读一本书30~60分钟。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["독서", "책읽기", "빌게이츠", "책", "정독", "독서1시간"],
            "en": ["reading", "read a book", "read 1 hour", "bill gates", "read 30m"],
            "ja": ["読書", "本を読む", "ビルゲイツ", "精読", "1時間読書"],
            "zh": ["阅读", "读书", "看书", "精读", "比尔盖茨"],
        },
    },
    {
        "id": 18, "domain": 4, "difficulty": "⭐⭐⭐",
        "role": {"ko": "리처드 파인만", "en": "Richard Feynman", "ja": "リチャード・ファインマン", "zh": "理查德·费曼"},
        "name": {
            "ko": "리처드 파인만의 파인만 테크닉 (쉬운 설명법)",
            "en": "The Feynman Technique (Teach Simply)",
            "ja": "ファインマン・テクニック (平易な説明)",
            "zh": "费曼学习法 (用极简语言教会他人)",
        },
        "excel_name": {
            "ko": "파인만 테크닉 (중학생 설명법)",
            "en": "Feynman Technique (Plain Explanation)",
            "ja": "ファインマン・テクニック",
            "zh": "费曼技巧（简化讲授）",
        },
        "philosophy": {
            "ko": "초등학생이나 중학생에게 쉬운 일상 언어로 설명할 수 없다면 진짜 아는 게 아니다",
            "en": "If you cannot explain a concept simply, you do not understand it well enough.",
            "ja": "中学生に平易な言葉で説明できないなら、それは本当に理解していない証拠。",
            "zh": "如果无法用浅显的语言向孩子讲明白，说明你还没有真正掌握它。",
        },
        "protocol": {
            "ko": "새로 배운 개념을 쉬운 비유와 평이한 단어로 백지에 직접 강의하듯 정리",
            "en": "Explain newly learned ideas on a blank page using everyday metaphors without jargon.",
            "ja": "新しく学んだ概念を専門用語なしで白紙にわかりやすく講義するようにまとめる。",
            "zh": "在白纸上不用术语，用通俗比喻像讲课一样复述新概念。",
        },
        "freq": {"ko": "주 1~2회", "en": "1-2x / Week", "ja": "週1〜2回", "zh": "每周1~2次"},
        "keywords": {
            "ko": ["파인만", "설명하기", "쉬운설명", "개념정리", "백지복습"],
            "en": ["feynman", "explain simply", "teach back", "blank page", "simplify concept"],
            "ja": ["ファインマン", "わかりやすく説明", "概念整理", "白紙復習"],
            "zh": ["费曼学习法", "费曼", "用简单语言解释", "白纸复盘"],
        },
    },
    {
        "id": 19, "domain": 4, "difficulty": "⭐⭐",
        "role": {"ko": "레오나르도 다빈치", "en": "Leonardo da Vinci", "ja": "レオナルド・ダ・ヴィンチ", "zh": "列奥纳多·达·芬奇"},
        "name": {
            "ko": "레오나르도 다빈치의 일상 관찰 노트(코덱스)",
            "en": "Da Vinci's Daily Curiosity Notebook",
            "ja": "ダ・ヴィンチの日常観察ノート",
            "zh": "达·芬奇的日常观察笔记（手稿）",
        },
        "excel_name": {
            "ko": "일상 관찰 코덱스(스케치북) 기록",
            "en": "Daily Curiosity Codex & Sketches",
            "ja": "日常観察コーデックス記録",
            "zh": "日常观察手记与草图",
        },
        "philosophy": {
            "ko": "호기심을 시각화하고 관찰을 언어와 그림으로 기록하는 습관",
            "en": "Keen observation turned into sketches and notes multiplies creative breakthroughs.",
            "ja": "日常の好奇心を言葉やスケッチに記録する習慣が独創性を育む。",
            "zh": "将好奇心与细致观察通过文字和草图记录下来，激发跨界创造力。",
        },
        "protocol": {
            "ko": "궁금한 질문, 주변의 디테일한 관찰, 아이디어를 주머니 노트에 무제한 기록",
            "en": "Carry a pocket notebook or app to capture questions, observations, and sketches daily.",
            "ja": "気づいた疑問や周囲の観察・アイデアをポケットノートに日々書き留める。",
            "zh": "随身记录疑问、细节观察与创意灵感草图。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["관찰노트", "스케치", "아이디어메모", "다빈치", "호기심기록"],
            "en": ["curiosity note", "observation notebook", "sketchbook", "da vinci", "idea journal"],
            "ja": ["観察ノート", "スケッチブック", "アイデアメモ", "ダヴィンチ"],
            "zh": ["观察笔记", "灵感笔记", "素描本", "达芬奇", "好奇心记录"],
        },
    },
    {
        "id": 20, "domain": 4, "difficulty": "⭐⭐⭐",
        "role": {"ko": "나발 라비칸트", "en": "Naval Ravikant", "ja": "ナヴァル・ラヴィカント", "zh": "纳瓦尔·拉维坎特"},
        "name": {
            "ko": "나발 라비칸트의 고유 지식 복리 축적",
            "en": "Naval's Specific Knowledge Compounding",
            "ja": "ナヴァルの固有知識の複利蓄積",
            "zh": "纳瓦尔的专长知识复利积累",
        },
        "excel_name": {
            "ko": "지혜의 복리 누적 (Specific Knowledge)",
            "en": "Compounding Specific Knowledge",
            "ja": "固有知識の複利蓄積",
            "zh": "专长知识复利积累",
        },
        "philosophy": {
            "ko": "남들이 대체할 수 없는 나만의 고유한 지식과 호기심을 파고들어라",
            "en": "Follow authentic curiosity to build specific knowledge society cannot easily train others to do.",
            "ja": "他人が代替できない自分固有の知的好奇心を深く掘り下げて複利で蓄積せよ。",
            "zh": "深耕他人无法轻易替代的个人专长知识与独特好奇心。",
        },
        "protocol": {
            "ko": "유행을 따르기보다 진정으로 몰입되는 1가지 주제를 깊게 파고드는 독서",
            "en": "Go deep into foundational texts and craft skills fueled by genuine curiosity over hype.",
            "ja": "流行を追うのではなく、心から没頭できる1つの専門領域を深く学び続ける。",
            "zh": "不盲从流行热点，围绕真正痴迷的领域开展深耕学习。",
        },
        "freq": {"ko": "주간", "en": "Weekly", "ja": "週次", "zh": "每周"},
        "keywords": {
            "ko": ["고유지식", "나발", "전문지식", "심층탐구", "복리학습"],
            "en": ["specific knowledge", "naval", "deep learning", "foundational study", "domain mastery"],
            "ja": ["固有知識", "ナヴァル", "深層学習", "専門探究"],
            "zh": ["专长知识", "纳瓦尔", "深度学习", "底层知识", "复利学习"],
        },
    },
    # --- Domain 5: Relationships & Leadership (21..25) ---
    {
        "id": 21, "domain": 5, "difficulty": "⭐⭐",
        "role": {"ko": "데일 카네기", "en": "Dale Carnegie", "ja": "デール・カーネギー", "zh": "戴尔·卡内基"},
        "name": {
            "ko": "데일 카네기의 이름 부르기 & 80:20 경청",
            "en": "Dale Carnegie's Remember Names & Listen",
            "ja": "カーネギーの名呼び＆80:20傾聴",
            "zh": "卡内基的呼唤姓名与80:20倾听",
        },
        "excel_name": {
            "ko": "이름 기억하기 & 80:20 경청",
            "en": "Use Names & 80:20 Active Listening",
            "ja": "名前を呼ぶ＆80:20傾聴",
            "zh": "记住名字与80:20深度倾听",
        },
        "philosophy": {
            "ko": "모든 사람에게 자신의 이름은 가장 달콤하고 중요한 소리다",
            "en": "A person's name is the sweetest sound in any language, paired with genuine listening.",
            "ja": "人にとって自分の名前ほど心地よい響きはなく、真摯な傾聴が信頼を築く。",
            "zh": "对任何人来说，自己的名字都是世上最悦耳的声音，加之真诚倾听最能打动人心。",
        },
        "protocol": {
            "ko": "대화 시 상대의 이름을 3회 이상 부르고, 내 말은 20%만 하며 80% 경청하기",
            "en": "Use the other person's name naturally and listen 80% while speaking 20%.",
            "ja": "会話では相手の名前を自然に呼び、話す20%：聴く80%を意識する。",
            "zh": "交流时称呼对方姓名，并做到80%时间专注倾听、20%表达。",
        },
        "freq": {"ko": "매일 대화 시", "en": "Every Conversation", "ja": "会話ごと", "zh": "每次对话"},
        "keywords": {
            "ko": ["이름부르기", "경청", "카네기", "칭찬", "상대방존중", "듣기"],
            "en": ["active listening", "carnegie", "80:20 listening", "remembered name", "listened deeply"],
            "ja": ["傾聴", "カーネギー", "名前を呼ぶ", "80対20"],
            "zh": ["倾听", "卡内基", "记住名字", "多听少说", "尊重他人"],
        },
    },
    {
        "id": 22, "domain": 5, "difficulty": "⭐⭐⭐",
        "role": {"ko": "찰리 멍거", "en": "Charlie Munger", "ja": "チャーリー・マンガー", "zh": "查理·芒格"},
        "name": {
            "ko": "찰리 멍거의 역발상(Inversion) 검증",
            "en": "Charlie Munger's Inversion Thinking",
            "ja": "チャーリー・マンガーの逆算(Inversion)",
            "zh": "查理·芒格的逆向思维检查",
        },
        "excel_name": {
            "ko": "역발상(Inversion) 검증",
            "en": "Inversion Risk Check",
            "ja": "逆算思考(インバージョン)検証",
            "zh": "逆向思维防踩坑验证",
        },
        "philosophy": {
            "ko": "문제를 거꾸로 뒤집어 생각하라: 어떻게 성공할까보다 어떻게 파멸할까를 피해라",
            "en": "Invert, always invert: avoiding stupidity consistently beats chasing brilliance.",
            "ja": "常に逆から考えよ。どう成功するかより、どうすれば失敗するかを先に特定して避ける。",
            "zh": "反过来想，总是反过来想：避开愚蠢与失败往往比追求聪明更关键。",
        },
        "protocol": {
            "ko": "새로운 프로젝트 시작 시 '이것이 완전히 망하는 최악의 방법'을 미리 나열하고 방지",
            "en": "Before any big plan, list how it could fail catastrophically and engineer safeguards.",
            "ja": "計画を始める前に『失敗する最悪のパターン』を列挙し、事前に予防線を張る。",
            "zh": "启动重要项目前，先列出“必然导致失败的做法”并逐一设防。",
        },
        "freq": {"ko": "의사결정 시", "en": "Key Decisions", "ja": "意思決定時", "zh": "决策时"},
        "keywords": {
            "ko": ["역발상", "멍거", "거꾸로생각", "실패예방", "파멸피하기"],
            "en": ["inversion", "invert", "munger", "pre-mortem", "failure check"],
            "ja": ["逆算思考", "マンガー", "インバージョン", "失敗予防"],
            "zh": ["逆向思维", "芒格", "事前验尸", "避坑清单"],
        },
    },
    {
        "id": 23, "domain": 5, "difficulty": "⭐⭐⭐⭐",
        "role": {"ko": "제프 베조스", "en": "Jeff Bezos", "ja": "ジェフ・ベゾス", "zh": "杰夫·贝索斯"},
        "name": {
            "ko": "제프 베조스의 6쪽 내러티브 서술형 메모",
            "en": "Jeff Bezos's 6-Page Narrative Memo",
            "ja": "ベゾスの6ページ記述式メモ",
            "zh": "贝索斯的六页叙事备忘录",
        },
        "excel_name": {
            "ko": "파워포인트 금지 & 6쪽 내러티브 메모",
            "en": "Narrative Memo Over Slide Decks",
            "ja": "スライド禁止＆6ページ散文メモ",
            "zh": "禁用PPT改为清晰叙事文档",
        },
        "philosophy": {
            "ko": "파워포인트는 생각을 숨기지만, 서술형 글쓰기는 깊은 사고를 강제한다",
            "en": "Slide bullet points hide fuzzy thinking; full narrative prose enforces clarity.",
            "ja": "箇条書きスライドは曖昧さを隠すが、文章による叙述は論理的思考を強制する。",
            "zh": "幻灯片要点容易掩盖模糊思路，而完整叙事写作倒逼逻辑深度。",
        },
        "protocol": {
            "ko": "회의 전 안건을 완전한 문장의 6페이지 내러티브로 작성하고 30분간 정독 후 토론",
            "en": "Write key proposals in full clear sentences rather than vague bullet slides.",
            "ja": "会議資料を箇条書きではなく完全な文章のメモで書き、冒頭に黙読時間を設ける。",
            "zh": "用逻辑完整的书面叙事长文梳理重大提案，先静读再讨论。",
        },
        "freq": {"ko": "회의 시", "en": "Major Meetings", "ja": "会議時", "zh": "重要会议前"},
        "keywords": {
            "ko": ["서술형메모", "6페이지", "회의메모", "내러티브", "글로소통"],
            "en": ["narrative memo", "6 page memo", "six page", "written memo", "no slides"],
            "ja": ["6ページメモ", "散文メモ", "ナラティブ", "会議メモ"],
            "zh": ["六页备忘录", "叙事文档", "书面沟通", "长文提案"],
        },
    },
    {
        "id": 24, "domain": 5, "difficulty": "⭐⭐",
        "role": {"ko": "사이먼 시넥", "en": "Simon Sinek", "ja": "サイモン・シネック", "zh": "西蒙·斯涅克"},
        "name": {
            "ko": "사이먼 시넥의 Why(왜)부터 시작하는 소통",
            "en": "Simon Sinek's Start With Why",
            "ja": "サイモン・シネック『Whyから始めよ』",
            "zh": "西蒙·斯涅克的从“为什么”开始沟通",
        },
        "excel_name": {
            "ko": "Why(왜)부터 시작하는 소통",
            "en": "Golden Circle: Start With Why",
            "ja": "Why(なぜ)から始める対話",
            "zh": "黄金圈法则：从Why开始",
        },
        "philosophy": {
            "ko": "사람들은 '무엇을' 하는가가 아니라 '왜' 하는가에 감동하고 따른다",
            "en": "People don't buy what you do—they buy why you do it.",
            "ja": "人は『何をするか』ではなく『なぜそれをするか』に共感して動く。",
            "zh": "人们追随的不是你“做什么”，而是你“为什么而做”。",
        },
        "protocol": {
            "ko": "모든 지시나 제안 시 반드시 핵심 명분과 이유(Why)를 가장 먼저 설명",
            "en": "Begin every team proposal or goal by stating clear purpose and 'Why' before 'How'.",
            "ja": "提案や依頼をするとき、手順より先に目的と理由(Why)を明確に伝える。",
            "zh": "每次提出方案或委派任务，优先阐明背后的初心与原因(Why)。",
        },
        "freq": {"ko": "매일 업무 시", "en": "Daily Communication", "ja": "業務時", "zh": "日常工作中"},
        "keywords": {
            "ko": ["why", "골든서클", "이유설명", "명분공유", "사이먼시넥"],
            "en": ["start with why", "golden circle", "simon sinek", "explain why", "purpose first"],
            "ja": ["Whyから", "ゴールデンサークル", "サイモンシネック", "目的共有"],
            "zh": ["黄金圈", "为什么开始", "西蒙斯涅克", "先讲原因"],
        },
    },
    {
        "id": 25, "domain": 5, "difficulty": "⭐⭐⭐⭐",
        "role": {"ko": "레이 달리오", "en": "Ray Dalio", "ja": "レイ・ダリオ", "zh": "瑞·达利欧"},
        "name": {
            "ko": "레이 달리오의 극단적 진실성과 투명성",
            "en": "Ray Dalio's Radical Truth & Transparency",
            "ja": "ダリオの徹底的な透明性と率直さ",
            "zh": "达利欧的极度坦诚与透明反馈",
        },
        "excel_name": {
            "ko": "극단적 진실성과 투명성",
            "en": "Radical Transparency & Feedback",
            "ja": "極端な誠実さと透明性",
            "zh": "极度真实与透明原则",
        },
        "philosophy": {
            "ko": "에고(자아)를 내려놓고 현실의 냉정한 피드백을 수용해야 진화한다",
            "en": "Pain + Reflection = Progress; drop ego to face candid reality and evolve.",
            "ja": "エゴを手放し、現実の率直なフィードバックを受け入れることで成長できる。",
            "zh": "痛苦 + 反思 = 进步；放下自我防御，坦然接纳客观反馈。",
        },
        "protocol": {
            "ko": "실수나 문제 발생 시 은폐하지 않고 즉각 공유하며 '원인 분석 로그' 작성",
            "en": "Log mistakes openly without defensiveness and analyze root causes objectively.",
            "ja": "ミスや課題を隠さず素直に共有し、客観的な原因分析ログを残す。",
            "zh": "出现失误时不掩饰推诿，立即坦诚复盘并记录根因。",
        },
        "freq": {"ko": "문제 발생 시", "en": "Whenever Issues Arise", "ja": "問題発生時", "zh": "遇到问题时"},
        "keywords": {
            "ko": ["피드백수용", "실수공유", "투명성", "원인분석", "에고내려놓기"],
            "en": ["radical transparency", "radical truth", "candid feedback", "ego aside", "root cause"],
            "ja": ["フィードバック受け入れ", "透明性", "原因分析", "エゴ手放す"],
            "zh": ["极度坦诚", "接受反馈", "原因分析", "复盘错误", "透明沟通"],
        },
    },
    # --- Domain 6: Wealth & Finance (26..30) ---
    {
        "id": 26, "domain": 6, "difficulty": "⭐⭐⭐",
        "role": {"ko": "모건 하우절", "en": "Morgan Housel", "ja": "モーガン・ハウセル", "zh": "摩根·豪泽尔"},
        "name": {
            "ko": "모건 하우절의 지출 통제 & 자동 저축률 극대화",
            "en": "Morgan Housel's Savings Rate & Control",
            "ja": "ハウセルの支出管理＆貯蓄率最大化",
            "zh": "摩根·豪泽尔的消费克制与高储蓄率",
        },
        "excel_name": {
            "ko": "자유를 위한 지출 통제 (저축률 극대화)",
            "en": "Control Lifestyle & Maximize Savings",
            "ja": "自由のための支出管理＆高貯蓄",
            "zh": "克制欲望与最大化储蓄率",
        },
        "philosophy": {
            "ko": "진정한 부는 쓰지 않은 돈이며, 남에게 과시하지 않는 자유의 총량이다",
            "en": "Wealth is what you don't spend—the hidden freedom you buy with savings.",
            "ja": "本当の富とは見せびらかす消費ではなく、使わずに残した自由の総量である。",
            "zh": "真正的财富是你没有花掉的那部分钱，它兑换的是人生自主权。",
        },
        "protocol": {
            "ko": "소득의 최소 30~50%를 먼저 자동 저축/투자 시스템으로 격리 후 잔액으로 소비",
            "en": "Pay yourself first by automating savings before spending and avoiding impulse buys.",
            "ja": "収入の一部を自動で先取り貯蓄・投資に回し、衝動買いを防ぐ。",
            "zh": "收入先自动储蓄与定投，再量入为出，杜绝冲动消费。",
        },
        "freq": {"ko": "월간/매일", "en": "Monthly/Daily", "ja": "毎月/毎日", "zh": "每月/每日"},
        "keywords": {
            "ko": ["저축", "지출통제", "절약", "무지출", "충동구매방어", "하우절"],
            "en": ["savings", "save money", "frugal", "no impulse buy", "morgan housel", "budget"],
            "ja": ["貯蓄", "節約", "支出管理", "無駄遣い防止", "ハウセル"],
            "zh": ["储蓄", "攒钱", "控制消费", "零冲动消费", "豪泽尔"],
        },
    },
    {
        "id": 27, "domain": 6, "difficulty": "⭐⭐⭐⭐",
        "role": {"ko": "워런 버핏", "en": "Warren Buffett", "ja": "ウォーレン・バフェット", "zh": "沃伦·巴菲特"},
        "name": {
            "ko": "워런 버핏의 능력 범위(Circle of Competence) 고수",
            "en": "Buffett's Circle of Competence Discipline",
            "ja": "バフェットの能力の輪(Circle of Competence)",
            "zh": "巴菲特的坚守能力圈原则",
        },
        "excel_name": {
            "ko": "능력 범위(Circle of Competence) 고수",
            "en": "Stay Within Circle of Competence",
            "ja": "能力の輪を厳守する投資・判断",
            "zh": "坚守投资与决策能力圈",
        },
        "philosophy": {
            "ko": "자신이 완벽히 이해하지 못하는 유행이나 복잡한 파생 상품에는 절대 손대지 않는다",
            "en": "Know what you understand deeply, and stay far away from hype outside your circle.",
            "ja": "自分が完全に理解していない流行や複雑な投機には決して手を出さない。",
            "zh": "决不涉足自己无法彻底看懂的投机风口。",
        },
        "protocol": {
            "ko": "매수 전 '이 비즈니스가 10년 뒤에도 살아남을 이유'를 A4 한 장으로 명쾌하게 소명",
            "en": "Before committing capital, write clearly why you understand the asset over 10 years.",
            "ja": "投資や決断の前に『なぜ10年後も価値が残るか』を1ページに明快に書き出す。",
            "zh": "投入资金前写清“为什么它十年后依然具备护城河”的逻辑说明。",
        },
        "freq": {"ko": "투자 시", "en": "Before Investing", "ja": "投資時", "zh": "每次投资前"},
        "keywords": {
            "ko": ["능력범위", "아는것에만투자", "장기투자", "모르는것거절", "원칙고수"],
            "en": ["circle of competence", "long term invest", "stick to principles", "moat thesis"],
            "ja": ["能力の輪", "長期投資", "理解できる投資", "原則厳守"],
            "zh": ["能力圈", "长期投资", "护城河", "不碰不懂"],
        },
    },
    {
        "id": 28, "domain": 6, "difficulty": "⭐⭐",
        "role": {"ko": "보도 섀퍼", "en": "Bodo Schäfer", "ja": "ボード・シェーファー", "zh": "博多·舍费尔"},
        "name": {
            "ko": "보도 섀퍼의 황금알 거위 4대 통장 분리",
            "en": "Schaefer's Automated 4-Bucket Accounts",
            "ja": "シェーファーの黄金のガチョウ口座分割",
            "zh": "博多·舍费尔的下金蛋鹅账户分配",
        },
        "excel_name": {
            "ko": "황금알을 낳는 거위 통장 분리",
            "en": "Automated Cash-Flow Buckets",
            "ja": "自動振替・4口座資産バケット",
            "zh": "四账户自动财务分流系统",
        },
        "philosophy": {
            "ko": "지출용, 투자용, 자기계발용 통장을 분리하여 소비 충동을 원천 차단",
            "en": "Separate spending, investing, and emergency buckets automatically to safeguard your goose.",
            "ja": "生活・投資・学習・予備の口座を自動分割し、資産を生み出すガチョウを守る。",
            "zh": "将日常开销、投资生息与备用账户物理隔离，守护你的生蛋金鹅。",
        },
        "protocol": {
            "ko": "소득 발생 당일 고정비/투자/자기계발/예비비 4대 통장 자동이체 실행",
            "en": "Automate payday transfers across Fixed, Investment, Growth, and Reserve buckets.",
            "ja": "収入日に固定費・投資・自己投資・予備費の4口座へ自動振り分けを実施する。",
            "zh": "发薪日自动划分固定开支、投资理财、自我成长与应急储备账户。",
        },
        "freq": {"ko": "월간", "en": "Monthly", "ja": "毎月", "zh": "每月"},
        "keywords": {
            "ko": ["통장쪼개기", "자동이체", "예비비", "투자통장", "보도섀퍼"],
            "en": ["split accounts", "auto transfer", "emergency fund", "investment account", "goose"],
            "ja": ["口座分割", "自動振替", "予備資金", "投資口座"],
            "zh": ["分账户", "自动转账", "备用金", "投资账户", "鹅账户"],
        },
    },
    {
        "id": 29, "domain": 6, "difficulty": "⭐⭐⭐",
        "role": {"ko": "찰리 멍거", "en": "Charlie Munger", "ja": "チャーリー・マンガー", "zh": "查理·芒格"},
        "name": {
            "ko": "찰리 멍거의 복리 흐름 방해 금지 (잦은 매매 자제)",
            "en": "Munger's Never Interrupt Compounding",
            "ja": "マンガーの複利を邪魔しない規律",
            "zh": "芒格的绝不打断复利原则",
        },
        "excel_name": {
            "ko": "복리의 마법을 방해하지 않기",
            "en": "Never Interrupt Compounding",
            "ja": "複利の流れを邪魔しない忍耐",
            "zh": "不打断复利进程（克制频繁交易）",
        },
        "philosophy": {
            "ko": "불필요하게 매매를 자주 하거나 세금/수수료를 낭비하여 복리의 흐름을 끊지 마라",
            "en": "The first rule of compounding is to never interrupt it unnecessarily.",
            "ja": "複利の第一法則は、不要な売買でその流れを決して途中で断ち切らないこと。",
            "zh": "复利的第一法则就是：永远不要毫无必要地打断它。",
        },
        "protocol": {
            "ko": "장기 투자 자산에 대해 일일 시세를 확인하지 않고 장기 관점으로 보유",
            "en": "Avoid checking intraday quotes obsessively; let long-term positions compound calmly.",
            "ja": "長期資産の短期値動きを頻繁に確認せず、長期視点でどっしり保有する。",
            "zh": "戒掉盯盘习惯，对长期核心资产保持耐心持有。",
        },
        "freq": {"ko": "매일/주간", "en": "Daily/Weekly", "ja": "毎日/週次", "zh": "每日/每周"},
        "keywords": {
            "ko": ["복리", "매매자제", "장기보유", "시세안보기", "진득하게"],
            "en": ["compounding", "compound interest", "hold long term", "no overtrading", "ignore ticker"],
            "ja": ["複利", "長期保有", "相場見ない", "売買我慢"],
            "zh": ["复利", "长期持有", "不盯盘", "少折腾", "耐心持仓"],
        },
    },
    {
        "id": 30, "domain": 6, "difficulty": "⭐⭐⭐",
        "role": {"ko": "MJ 드마코", "en": "MJ DeMarco", "ja": "MJ・デマルコ", "zh": "MJ·德马科"},
        "name": {
            "ko": "MJ 드마코의 생산자 관점 분석",
            "en": "MJ DeMarco's Producer Mindset Audit",
            "ja": "MJデマルコの生産者視点分析",
            "zh": "MJ·德马科的生产者视角分析",
        },
        "excel_name": {
            "ko": "소비자 마인드에서 생산자 마인드로 전환",
            "en": "Producer Over Consumer Mindset",
            "ja": "消費者から生産者視点への転換",
            "zh": "从消费者思维转向生产者思维",
        },
        "philosophy": {
            "ko": "돈을 쓰는 입장에서 벗어나, 세상에 가치를 공급하고 문제를 해결하는 입장이 되라",
            "en": "Shift from passive consumer to value creator who solves real market problems.",
            "ja": "消費する側から、価値を提供して人の課題を解決する生産者側へ視点を移せ。",
            "zh": "摆脱纯消费视角，站在提供价值与解决问题的生产者视角思考。",
        },
        "protocol": {
            "ko": "무언가를 소비할 때마다 '이 생산자는 어떻게 돈을 벌고 구조를 짰는가?' 역분석",
            "en": "Reverse-engineer products you use: ask what pain they solve and how the system scales.",
            "ja": "何かを購入・利用するたびに『提供者はどう価値と仕組みを作ったか』を分析する。",
            "zh": "每次使用优秀产品时逆向拆解：它解决了什么痛点、商业闭环如何设计。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["생산자관점", "비즈니스분석", "가치제공", "역발상수익구조", "드마코"],
            "en": ["producer mindset", "value creation", "business analysis", "reverse engineer", "demarco"],
            "ja": ["生産者視点", "ビジネス分析", "価値提供", "デマルコ"],
            "zh": ["生产者思维", "商业拆解", "创造价值", "德马科"],
        },
    },
    # --- Domain 7: Systems & Routines (31..35) ---
    {
        "id": 31, "domain": 7, "difficulty": "⭐",
        "role": {"ko": "제임스 클리어", "en": "James Clear", "ja": "ジェームズ・クリアー", "zh": "詹姆斯·克利尔"},
        "name": {
            "ko": "제임스 클리어의 2분 규칙 (극단적으로 쉬운 시작)",
            "en": "James Clear's 2-Minute Rule",
            "ja": "クリアーの2分ルール (スモールスタート)",
            "zh": "詹姆斯·克利尔的2分钟启动法则",
        },
        "excel_name": {
            "ko": "2분 규칙 (Two-Minute Rule)",
            "en": "Two-Minute Rule (Start Easy)",
            "ja": "2分間ルール（すぐ着手）",
            "zh": "两分钟起步法则",
        },
        "philosophy": {
            "ko": "새로운 습관을 시작할 때는 2분 이내에 끝낼 수 있을 정도로 극단적으로 쉽게 만들어라",
            "en": "Scale any daunting habit down to a two-minute gateway action to beat resistance.",
            "ja": "新しい習慣は『2分以内で始められるほど小さくする』ことで抵抗感をゼロにできる。",
            "zh": "把任何新习惯缩小到两分钟内就能启动的微小动作，消除拖延阻力。",
        },
        "protocol": {
            "ko": "운동하기 대신 '운동화 끈 매기', 책 1권 읽기 대신 '책 1쪽 펼치기'로 즉각 시작",
            "en": "Start immediately by shrinking tasks: lace shoes or read 1 page to build momentum.",
            "ja": "『運動する』ではなく『靴を履く』、『本を読む』ではなく『1ページ開く』ですぐ始める。",
            "zh": "用极小动作破冰：比如穿好跑鞋或打开书读1页。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["2분규칙", "2분", "작게시작", "아주작은습관", "즉시실행", "시작하기"],
            "en": ["two minute rule", "2 minute rule", "2m rule", "start small", "just 2 min"],
            "ja": ["2分ルール", "小さく始める", "すぐ着手", "スモールスタート"],
            "zh": ["2分钟法则", "两分钟法则", "微习惯起步", "立即开始"],
        },
    },
    {
        "id": 32, "domain": 7, "difficulty": "⭐⭐",
        "role": {"ko": "제임스 클리어", "en": "James Clear", "ja": "ジェームズ・クリアー", "zh": "詹姆斯·克利尔"},
        "name": {
            "ko": "제임스 클리어의 습관 쌓기 (기존 습관 + 새 습관)",
            "en": "James Clear's Habit Stacking",
            "ja": "クリアーのハビット・スタッキング",
            "zh": "詹姆斯·克利尔的习惯叠加法",
        },
        "excel_name": {
            "ko": "습관 쌓기 (Habit Stacking)",
            "en": "Habit Stacking Anchor",
            "ja": "習慣の積み重ね (スタッキング)",
            "zh": "习惯叠加锚定 (Habit Stacking)",
        },
        "philosophy": {
            "ko": "이미 매일 하고 있는 기존 습관 바로 뒤에 새로운 습관을 붙여라",
            "en": "Anchor a new habit directly onto an existing automatic routine.",
            "ja": "すでに毎日行っている既存の習慣の直後に、新しい習慣を連結させる。",
            "zh": "将新习惯直接锚定在已经固化的日常动作之后。",
        },
        "protocol": {
            "ko": "[커피를 마신 직후] + [영양제를 챙겨 먹는다], [양치 후] + [스쿼트 10회]",
            "en": "Follow 'After [CURRENT HABIT], I will [NEW HABIT]' consistently each day.",
            "ja": "『朝コーヒーを飲んだ直後に5分メモを書く』のように既存習慣に紐づける。",
            "zh": "使用句式：在【现有习惯】之后，立刻做【新习惯】。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["습관쌓기", "습관연계", "연쇄루틴", "식사후", "기상후"],
            "en": ["habit stack", "habit stacking", "after coffee", "cue anchor"],
            "ja": ["習慣積み上げ", "ハビットスタッキング", "習慣連鎖", "既存習慣"],
            "zh": ["习惯叠加", "习惯串联", "微习惯链", "习惯绑定"],
        },
    },
    {
        "id": 33, "domain": 7, "difficulty": "⭐⭐",
        "role": {"ko": "벤자민 프랭클린", "en": "Benjamin Franklin", "ja": "B・フランクリン", "zh": "本杰明·富兰克林"},
        "name": {
            "ko": "벤자민 프랭클린의 아침 자문 & 저녁 회고",
            "en": "Ben Franklin's AM/PM Self-Reflection",
            "ja": "フランクリンの朝問＆夜反省ルーティン",
            "zh": "富兰克林的早间自问与晚间复盘",
        },
        "excel_name": {
            "ko": "아침의 질문 & 저녁의 회고",
            "en": "Morning Question & Evening Review",
            "ja": "朝の問いかけ＆夜の振り返り",
            "zh": "晨间规划与睡前自省",
        },
        "philosophy": {
            "ko": "계획 없는 하루는 표류하는 배와 같으며, 회고 없는 행동은 개선되지 않는다",
            "en": "What good shall I do today? What good have I done today?",
            "ja": "計画なき一日は漂流する船であり、振り返りなき行動は磨かれない。",
            "zh": "没有规划的一天如随波逐流，缺乏复盘则难以持续精进。",
        },
        "protocol": {
            "ko": "아침: '오늘 내가 실천할 선한 일은?', 저녁: '오늘 내가 실천한 선한 일은?' 자문",
            "en": "Morning: set intention ('What good shall I do?'); Night: review ('What went well?').",
            "ja": "朝に『今日なすべき善きことは何か』、夜に『今日成し遂げたことは何か』を自問する。",
            "zh": "早晨自问“今日要完成什么善事”，夜晚复盘“今日收获与改进”。",
        },
        "freq": {"ko": "매일(아침/저녁)", "en": "Daily (AM/PM)", "ja": "朝晩毎日", "zh": "每日早晚"},
        "keywords": {
            "ko": ["프랭클린", "아침질문", "저녁회고", "선한일", "하루점검"],
            "en": ["franklin", "evening review", "daily reflection", "what good shall i do", "morning question"],
            "ja": ["フランクリン", "朝の質問", "夜の振り返り", "日次反省"],
            "zh": ["富兰克林", "早间提问", "晚间复盘", "每日自省"],
        },
    },
    {
        "id": 34, "domain": 7, "difficulty": "⭐⭐",
        "role": {"ko": "팀 페리스 / 칼 뉴포트", "en": "Cal Newport / Tim Ferriss", "ja": "ニューポート/フェリス", "zh": "纽波特 / 费里斯"},
        "name": {
            "ko": "팀 페리스의 저녁 셧다운 의식 (공식 업무 종료)",
            "en": "Cal Newport's Work Shutdown Ritual",
            "ja": "夕方の仕事シャットダウン儀式",
            "zh": "下班工作关机与精力隔离仪式",
        },
        "excel_name": {
            "ko": "저녁 셧다운 의식 (Shutdown Routine)",
            "en": "End-of-Day Shutdown Ritual",
            "ja": "業務シャットダウン儀式",
            "zh": "晚间工作彻底收工仪式",
        },
        "philosophy": {
            "ko": "퇴근 후 일에 대한 미련과 인지적 부하를 닫아야 진정한 뇌 휴식이 가능",
            "en": "A crisp end-of-day shutdown lets your nervous system truly recover overnight.",
            "ja": "仕事終わりの明確な区切りが、脳の残留負荷(注意残留)を断ち切り回復を促す。",
            "zh": "为一天的工作画上清晰句号，才能彻底释放大脑认知残留。",
        },
        "protocol": {
            "ko": "퇴근 10분 전 내일의 3대 과제 메모 후 '업무 공식 종료'를 소리내어 선언",
            "en": "Jot down tomorrow's top 3 tasks before closing your laptop and declare work complete.",
            "ja": "終業10分前に明日の最重要3タスクをメモし、仕事終了を明確に区切る。",
            "zh": "下班前10分钟列好明日前三要事，随后宣布“今日工作完成”。",
        },
        "freq": {"ko": "매일(저녁)", "en": "Daily (PM)", "ja": "毎夕", "zh": "每日下班"},
        "keywords": {
            "ko": ["셧다운", "업무종료", "퇴근의식", "내일할일정리", "뇌휴식"],
            "en": ["shutdown ritual", "work shutdown", "finished work", "end of workday", "closed laptop"],
            "ja": ["シャットダウン", "仕事終了", "退勤儀式", "明日のタスク整理"],
            "zh": ["关机仪式", "结束工作", "下班仪式", "收工复盘"],
        },
    },
    {
        "id": 35, "domain": 7, "difficulty": "⭐⭐⭐",
        "role": {"ko": "아토믹 시스템", "en": "Atomic Systems Design", "ja": "アトミック設計", "zh": "环境设计法则"},
        "name": {
            "ko": "아토믹 시스템의 환경 디자인 (좋은 습관 마찰 0)",
            "en": "Environment Design (Zero Friction)",
            "ja": "行動摩擦ゼロの環境デザイン",
            "zh": "零阻力好习惯环境设计",
        },
        "excel_name": {
            "ko": "환경 디자이너 되기",
            "en": "Frictionless Environment Architecture",
            "ja": "環境デザイナーになる",
            "zh": "成为环境设计师",
        },
        "philosophy": {
            "ko": "의지력에 의존하지 말고, 좋은 습관은 마찰을 0으로, 나쁜 습관은 마찰을 100으로",
            "en": "Willpower fades; make good habits effortless and bad habits inconvenient.",
            "ja": "意志力に頼らず、良い習慣の摩擦を0に・悪い習慣の摩擦を100に設計する。",
            "zh": "不要迷信意志力：让好习惯零阻力启动，让坏习惯阻力最大化。",
        },
        "protocol": {
            "ko": "공부할 땐 책상 위 휴대폰을 다른 방으로 치우고, 아침 운동복은 머리맡에 미리 배치",
            "en": "Leave workout clothes/books visible and place phone charger in another room.",
            "ja": "勉強中はスマホを別室に置き、運動着や本はすぐ手に取れる位置へ事前配置する。",
            "zh": "工作时把手机放去另一间房，运动服与好书放在触手可及之处。",
        },
        "freq": {"ko": "매일", "en": "Daily", "ja": "毎日", "zh": "每日"},
        "keywords": {
            "ko": ["환경디자인", "마찰력", "휴대폰치우기", "운동복배치", "환경세팅"],
            "en": ["environment design", "zero friction", "phone in another room", "cue setup", "prep workspace"],
            "ja": ["環境デザイン", "摩擦ゼロ", "環境設計", "スマホ別室"],
            "zh": ["环境设计", "减少阻力", "手机放客厅", "环境搭建"],
        },
    },
]


def get_habits_catalog(lang: str = None) -> list:
    """Return all 35 habits formatted cleanly for the requested/active language."""
    resolved = resolve_language(lang)
    out = []
    for raw in RAW_HABITS:
        dom = DOMAINS[raw["domain"]]
        out.append({
            "id": raw["id"],
            "domain_id": raw["domain"],
            "domain_code": dom["code"],
            "category": dom["category"][resolved],
            "sheet_domain": dom["sheet_domain"][resolved],
            "role_model": raw["role"][resolved],
            "name": raw["name"][resolved],
            "excel_name": raw["excel_name"][resolved],
            "philosophy": raw["philosophy"][resolved],
            "protocol": raw["protocol"][resolved],
            "frequency": raw["freq"][resolved],
            "difficulty": raw["difficulty"],
            "keywords": list(raw["keywords"][resolved]),
            "all_keywords": [
                kw
                for lc in SUPPORTED_LANGUAGES
                for kw in raw["keywords"].get(lc, [])
            ],
        })
    return out


def get_domain_rows(lang: str = None) -> list:
    """Return ordered metadata for the 7 domains for Dashboard summary rows."""
    resolved = resolve_language(lang)
    rows = []
    for dom_id in range(1, 8):
        d = DOMAINS[dom_id]
        rows.append({
            "id": dom_id,
            "code": d["code"],
            "sheet_domain": d["sheet_domain"][resolved],
            "gurus": d["gurus"][resolved],
        })
    return rows
