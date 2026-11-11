"""
=============================================================================
🧠 ALL-IN-ONE LIFE OS : Localized Role-Model Mentor Personas (4 Languages)
=============================================================================
Provides mentor profiles and localized nudge / praise / action / postpone templates
across Korean (ko), English (en), Japanese (ja), and Simplified Chinese (zh).
=============================================================================
"""

from i18n import resolve_language

PERSONAS_BY_LANG = {
    "ko": {
        "huberman": {
            "name": "앤드루 후버만 박사",
            "title": "⚡ 앤드루 후버만 (신경과학/생체리듬)",
            "emoji": "🔬",
            "nudge_templates": [
                "도파민 기준선과 생체시계를 점검할 시간입니다. 오늘 [{name}] 실천하셨습니까?",
                "신경가소성을 활성화하세요. 오늘 [{name}] 프로토콜은 진행하셨나요?",
                "스트레스 회복력과 코르티솔 리듬을 위해, 오늘 [{name}] 확인해 보셨습니까?",
            ],
            "praise_templates": [
                "탁월합니다! '{name}' 실천으로 신경회로와 도파민 보상 시스템이 최적으로 동기화되었습니다.",
                "훌륭한 생체 프로토콜입니다! '{name}'을(를) 완수하여 지속 가능한 에너지 기준선이 구축되었습니다.",
            ],
            "doing_now_templates": [
                "즉각 착수하십시오! 뇌는 행동을 시작할 때 비로소 노르에피네프린을 분비하여 집중 모드로 전환됩니다. 2분만 밀어붙이세요!",
                "좋습니다! 지금 바로 2분만 실행하세요. 신경계가 즉시 적응할 것입니다.",
            ],
            "postpone_templates": [
                "인지적 과부하를 피하는 것도 과학입니다. 잠시 휴식 후 신경계가 안정되면 다시 리마인드하겠습니다.",
            ],
        },
        "buffett": {
            "name": "워런 버핏 회장",
            "title": "💼 워런 버핏 (5/25 우선순위 & 복리)",
            "emoji": "📈",
            "nudge_templates": [
                "인생의 20가지 잡무에 시간을 빼앗기지 마세요. 오늘 최우선 과제 [{name}]은 챙기셨습니까?",
                "탁월함은 매일 복리로 쌓입니다. 오늘 [{name}] 원칙을 지키셨나요?",
                "능력 범위(Circle of Competence)에 집중하세요. [{name}] 실행 여부를 점검할 때입니다.",
            ],
            "praise_templates": [
                "현명한 투자입니다! '{name}'을(를) 지켜냄으로써 인생의 장기 복리 계좌에 큰 자산이 쌓였습니다.",
                "단호한 원칙 준수입니다! '{name}' 실천 완료로 오늘의 핵심 승리를 확보하셨습니다.",
            ],
            "doing_now_templates": [
                "망설이지 말고 지금 착수하세요! 가장 중요한 5대 과제에 먼저 자본과 시간을 배분하는 것이 투자의 제1법칙입니다.",
                "지금 바로 시작하세요. 2분의 작은 집중이 10년 뒤의 엄청난 차이를 만듭니다.",
            ],
            "postpone_templates": [
                "알겠습니다. 다만 불필요한 유혹 때문에 미루는 것은 아닌지 스스로에게 솔직해지세요. 잠시 후 다시 확인하겠습니다.",
            ],
        },
        "musk_grok": {
            "name": "일론 머스크 & Grok",
            "title": "🚀 일론 머스크 & Grok (제1원칙 & 팩트)",
            "emoji": "⚡",
            "nudge_templates": [
                "관행과 핑계는 물리 법칙 앞에서는 제로입니다. 오늘 [{name}] 하셨습니까?",
                "타임박스를 타이트하게 쪼개세요! 오늘 [{name}] 완료 체크하셨나요?",
                "인류를 다행성 종족으로 만들려면 기본부터 해야죠. [{name}] 실행하셨습니까? (웃음)",
            ],
            "praise_templates": [
                "로켓 엔진 점화 완료! '{name}'을(를) 멋지게 격파하셨습니다. 생산성 가속도가 붙고 있군요!",
                "제1원칙에 부합하는 완벽한 실행입니다. '{name}' 완료! 계속 풀 스로틀로 밀어붙이세요.",
            ],
            "doing_now_templates": [
                "말보단 실행입니다! 지금 당장 5분 타임박스를 걸고 불도저처럼 착수하세요. 시작하면 관성이 붙습니다!",
                "지금 바로 착수하세요. 복잡한 생각 버리고 2분 안에 첫 줄을 긋는 겁니다. 레츠고!",
            ],
            "postpone_templates": [
                "지연은 혁신의 적이지만... 좋습니다, 배터리 충전 시간으로 인정하죠. 30분 뒤에 다시 묻겠습니다!",
            ],
        },
        "aurelius": {
            "name": "마르쿠스 아우렐리우스 황제",
            "title": "🧠 마르쿠스 아우렐리우스 (스토아 평정심)",
            "emoji": "🏛️",
            "nudge_templates": [
                "그대의 영혼을 가꾸는 시간입니다. 오늘 [{name}] 실천을 잊지 않으셨습니까?",
                "통제할 수 있는 것에 전념하십시오. 오늘 [{name}]은(는) 그대의 선택에 달려 있습니다.",
                "하루를 시작하며 선한 의무를 다하고 계십니까? [{name}] 실천을 점검하십시오.",
            ],
            "praise_templates": [
                "고결한 품격입니다. '{name}'의 실천으로 그대 내면의 신전에 흔들리지 않는 평정이 깃들었습니다.",
                "외부의 소음에 흔들리지 않고 스스로와의 약속 '{name}'을(를) 지켜내셨군요. 훌륭합니다.",
            ],
            "doing_now_templates": [
                "주저하지 말고 바로 그대에게 주어진 선한 일을 행하십시오. 현재라는 순간만이 온전히 그대의 것입니다.",
                "지금 바로 시작하십시오. 작은 행동 하나가 그대의 존엄을 증명합니다.",
            ],
            "postpone_templates": [
                "마음의 평정을 잃지 마십시오. 호흡을 가다듬고 영혼이 준비되었을 때 다시 부르겠습니다.",
            ],
        },
    },
    "en": {
        "huberman": {
            "name": "Dr. Andrew Huberman",
            "title": "⚡ Andrew Huberman (Neuroscience & Circadian)",
            "emoji": "🔬",
            "nudge_templates": [
                "Time to calibrate your dopamine baseline and circadian clock. Have you practiced [{name}] today?",
                "Engage neuroplasticity now. Did you complete the [{name}] protocol today?",
                "For stress resilience and cortisol rhythm, have you checked off [{name}] today?",
            ],
            "praise_templates": [
                "Outstanding! Practicing '{name}' synchronizes your neural circuits and sustains your dopamine baseline.",
                "Solid biological protocol! Completing '{name}' locks in durable focus and energy.",
            ],
            "doing_now_templates": [
                "Initiate immediately! Action triggers norepinephrine release, shifting your brain into focus mode. Push for 2 minutes!",
                "Let's go—start with just 2 minutes right now. Your nervous system will adapt fast.",
            ],
            "postpone_templates": [
                "Managing cognitive load is also good science. Take a brief reset, and I will check back soon.",
            ],
        },
        "buffett": {
            "name": "Warren Buffett",
            "title": "💼 Warren Buffett (5/25 Focus & Compounding)",
            "emoji": "📈",
            "nudge_templates": [
                "Don't let the bottom 20 tasks steal your day. Have you handled top priority [{name}] today?",
                "Excellence compounds daily. Did you stick to your [{name}] principle today?",
                "Stay inside your Circle of Competence. Is [{name}] checked off today?",
            ],
            "praise_templates": [
                "Wise investment! Keeping '{name}' adds a durable asset to your life's compounding ledger.",
                "Disciplined execution! Finishing '{name}' secures a key win for today.",
            ],
            "doing_now_templates": [
                "Do not hesitate—allocate your time to your top 5 priorities first. That is Rule #1!",
                "Start right now. Two focused minutes compound enormously over ten years.",
            ],
            "postpone_templates": [
                "Understood. Just be honest with yourself whether distraction is creeping in—we will revisit this soon.",
            ],
        },
        "musk_grok": {
            "name": "Elon Musk & Grok",
            "title": "🚀 Elon Musk & Grok (First Principles)",
            "emoji": "⚡",
            "nudge_templates": [
                "Excuses mean zero against physics. Did you execute [{name}] today?",
                "Tighten your timeboxes! Have you knocked out [{name}] yet?",
                "To make humanity multiplanetary, we nail the basics first. [{name}] done?",
            ],
            "praise_templates": [
                "Liftoff confirmed! Crushing '{name}' accelerates your daily execution velocity.",
                "Pure first-principles execution on '{name}'! Keep it at full throttle.",
            ],
            "doing_now_templates": [
                "Less talk, more execution! Set a 5-minute timebox and punch through it right now.",
                "Drop the overthinking—ship the first step in 2 minutes. Let's go!",
            ],
            "postpone_templates": [
                "Delay is the enemy of progress... fair enough, recharge batteries and we check again in 30 minutes!",
            ],
        },
        "aurelius": {
            "name": "Marcus Aurelius",
            "title": "🧠 Marcus Aurelius (Stoic Equanimity)",
            "emoji": "🏛️",
            "nudge_templates": [
                "Tend to your inner citadel. Have you practiced [{name}] today?",
                "Focus solely on what is in your control. Completing [{name}] rests in your hands today.",
                "Are you fulfilling your duty to yourself? Take a moment to check [{name}].",
            ],
            "praise_templates": [
                "Noble restraint and poise. Practicing '{name}' strengthens the quiet fortress within.",
                "Unshaken by external noise, you honored your promise of '{name}'. Well done.",
            ],
            "doing_now_templates": [
                "Do not delay the good work placed before you. The present moment alone belongs to you.",
                "Begin at once. One small deliberate action proves your dignity.",
            ],
            "postpone_templates": [
                "Preserve your composure. Catch your breath, and return when your mind is steady.",
            ],
        },
    },
    "ja": {
        "huberman": {
            "name": "アンドリュー・フーバーマン博士",
            "title": "⚡ フーバーマン博士 (神経科学/生体リズム)",
            "emoji": "🔬",
            "nudge_templates": [
                "ドーパミン基準値と体内時計を整える時間です。今日 [{name}] は実践しましたか？",
                "神経可塑性を高めましょう。本日の [{name}] プロトコルは進みましたか？",
                "ストレス回復力とコルチゾールリズムのために、今日 [{name}] を確認しましたか？",
            ],
            "praise_templates": [
                "卓越しています！「{name}」の実践により神経回路とドーパミン報酬系が最適に同期しました。",
                "見事な生体プロトコルです！「{name}」の完了で持続可能なエネルギー基準が整いました。",
            ],
            "doing_now_templates": [
                "今すぐ着手しましょう！行動を起こすとノルアドレナリンが分泌され集中モードに切り替わります。まず2分だけ！",
                "いい判断です！まずは2分だけ実行してください。神経系が即座に適応します。",
            ],
            "postpone_templates": [
                "認知的過負荷を避けることも科学です。少し休んで神経系が落ち着いたらまたリマインドします。",
            ],
        },
        "buffett": {
            "name": "ウォーレン・バフェット会長",
            "title": "💼 ウォーレン・バフェット (5/25集中＆複利)",
            "emoji": "📈",
            "nudge_templates": [
                "人生の不要な20の雑務に時間を奪われてはいけません。最優先課題 [{name}] は済みましたか？",
                "卓越さは毎日複利で積み上がります。今日 [{name}] の原則を守れましたか？",
                "能力の輪に集中してください。[{name}] の実行を確認する時間です。",
            ],
            "praise_templates": [
                "賢明な投資です！「{name}」を守り抜いたことで、人生の長期複利口座に大きな資産が積まれました。",
                "ぶれない原則の勝利です！「{name}」完了で今日の重要な一歩を確保しました。",
            ],
            "doing_now_templates": [
                "迷わず今すぐ取りかかりましょう！最重要5項目に時間を配分することが投資の第一原則です。",
                "今すぐ始めてください。2分の小さな集中が10年後に圧倒的な差を生みます。",
            ],
            "postpone_templates": [
                "承知しました。ただ誘惑に負けて先延ばししていないか自問しつつ、また後で確認しましょう。",
            ],
        },
        "musk_grok": {
            "name": "イーロン・マスク & Grok",
            "title": "🚀 イーロン・マスク & Grok (第一原理思考)",
            "emoji": "⚡",
            "nudge_templates": [
                "言い訳は物理法則の前ではゼロです。今日 [{name}] を実行しましたか？",
                "タイムボックスをタイトに刻みましょう！[{name}] は完了チェック済みですか？",
                "基本を徹底してこそ大きな挑戦ができます。[{name}] 実行しましたか？",
            ],
            "praise_templates": [
                "ロケット点火完了！「{name}」を見事に突破しました。生産性の加速度が上がっています！",
                "第一原理に沿った完璧な実行です。「{name}」完了！そのままフルスロットルで行きましょう。",
            ],
            "doing_now_templates": [
                "言葉より実行です！今すぐ5分タイムボックスを設定して突破しましょう。",
                "迷いは捨てて2分以内に最初の1行を踏み出しましょう。レッツゴー！",
            ],
            "postpone_templates": [
                "遅延は進歩の敵ですが…充電時間として認めましょう。30分後にまた確認します！",
            ],
        },
        "aurelius": {
            "name": "マルクス・アウレリウス",
            "title": "🧠 マルクス・アウレリウス (ストア派の不動心)",
            "emoji": "🏛️",
            "nudge_templates": [
                "内なる砦を養う時です。今日 [{name}] の実践を忘れていませんか？",
                "自らの制御できることだけに専念せよ。[{name}] を行うかどうかはあなたの選択です。",
                "今日の善き務めを果たしていますか？ [{name}] の実践を点検しましょう。",
            ],
            "praise_templates": [
                "気高き品格です。「{name}」の実践によって内なる神殿に揺るぎない静穏が宿りました。",
                "外の雑音に惑わされず自己との約束「{name}」を守り抜きましたね。見事です。",
            ],
            "doing_now_templates": [
                "ためらわず、目の前に与えられた善き行いを今すぐ実行しなさい。現在という瞬間だけがあなたのものです。",
                "今すぐ始めなさい。ひとつの小さな行動があなたの尊厳を証明します。",
            ],
            "postpone_templates": [
                "心の平穏を失わないように。呼吸を整え、魂が整った時にまた呼びかけましょう。",
            ],
        },
    },
    "zh": {
        "huberman": {
            "name": "安德鲁·休伯曼博士",
            "title": "⚡ 安德鲁·休伯曼 (神经科学与节律)",
            "emoji": "🔬",
            "nudge_templates": [
                "是时候校准您的多巴胺基线与昼夜节律了。今天实践了 [{name}] 吗？",
                "激活神经可塑性！今天完成 [{name}] 这项协议了吗？",
                "为了皮质醇节律和抗压恢复力，今天确认过 [{name}] 了吗？",
            ],
            "praise_templates": [
                "非常出色！实践“{name}”让神经回路与多巴胺奖赏系统达到了最佳同步。",
                "极佳的生理节律执行！完成“{name}”将建立更持久的能量基线。",
            ],
            "doing_now_templates": [
                "立即开始！大脑只有在开始行动后才会分泌去甲肾上腺素并进入专注状态，坚持2分钟！",
                "很好！现在就只做2分钟，您的神经系统会迅速适应。",
            ],
            "postpone_templates": [
                "避免认知过载也是科学之道。短暂休息后我再提醒您。",
            ],
        },
        "buffett": {
            "name": "沃伦·巴菲特",
            "title": "💼 沃伦·巴菲特 (5/25优先级与复利)",
            "emoji": "📈",
            "nudge_templates": [
                "别让其余20件琐事吞噬您的时间。今天的首要事项 [{name}] 落实了吗？",
                "卓越来自日复一日的复利。今天坚持了 [{name}] 原则吗？",
                "聚焦于您的能力圈内。该检查 [{name}] 的执行情况了。",
            ],
            "praise_templates": [
                "明智的投资！守住“{name}”，等于为您的人生长期复利账户注入优质资产。",
                "坚定的原则执行！完成“{name}”锁定了今天的焦点胜利。",
            ],
            "doing_now_templates": [
                "不要犹豫，马上动手！优先将精力分配给最重要的5件事是投资第一法则。",
                "现在就开始。2分钟的小专注会在十年后产生巨大差距。",
            ],
            "postpone_templates": [
                "好的，但请诚实审视自己是否被无关诱惑分散了精力。稍后再与您确认。",
            ],
        },
        "musk_grok": {
            "name": "埃隆·马斯克 & Grok",
            "title": "🚀 埃隆·马斯克 & Grok (第一性原理)",
            "emoji": "⚡",
            "nudge_templates": [
                "借口在物理定律面前一文不值。今天执行 [{name}] 了吗？",
                "把时间盒切得更紧凑些！[{name}] 打卡完成了吗？",
                "改变世界也要从夯实基础开始。[{name}] 完成了吗？",
            ],
            "praise_templates": [
                "火箭引擎点火成功！攻克“{name}”让您的每日效率加速度飙升！",
                "完全符合第一性原理的执行！“{name}”完成，继续全速推进！",
            ],
            "doing_now_templates": [
                "少说多做！立刻设定5分钟时间盒像推土机一样推进。动起来就会有惯性！",
                "别想太多，2分钟内先迈出第一步。Let's go!",
            ],
            "postpone_templates": [
                "拖延虽然是创新的敌人……好吧，算作充电时间，30分钟后再问您！",
            ],
        },
        "aurelius": {
            "name": "马可·奥勒留",
            "title": "🧠 马可·奥勒留 (斯多葛内心平静)",
            "emoji": "🏛️",
            "nudge_templates": [
                "修缮您内心的城堡吧。今天没有忘记践行 [{name}] 吧？",
                "只专注于您能掌控之事。今天是否完成 [{name}] 完全取决于您的选择。",
                "今天是否履行了对自己的善意承诺？请检查 [{name}]。",
            ],
            "praise_templates": [
                "高尚的品格。“{name}”的践行让您内心的圣殿保持坚定而平静。",
                "不为外界喧嚣所动，信守了与自己的约定“{name}”。做得好。",
            ],
            "doing_now_templates": [
                "不要迟疑，立即去做摆在面前的善行。唯有此刻完全属于您。",
                "现在就开始。一个微小而坚定的行动足以证明您的尊严。",
            ],
            "postpone_templates": [
                "切勿失去内心的平静。调整呼吸，待心境稳固时我再唤醒您。",
            ],
        },
    },
}


def get_personas(lang: str = None) -> dict:
    resolved = resolve_language(lang)
    return PERSONAS_BY_LANG.get(resolved, PERSONAS_BY_LANG["en"])
