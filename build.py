#!/usr/bin/env python3
"""Build a readable, dependency-free static page from the Chinese content source."""
import html
import re
from pathlib import Path
from src.guide_data import groups

ROOT = Path(__file__).resolve().parent
SOURCES = [
('NHLBI / NIH · 失眠的原因与风险因素','https://www.nhlbi.nih.gov/health/insomnia/causes','压力、遗传、环境与生活方式。'),
('NHS · 失眠','https://www.nhs.uk/conditions/insomnia/','常见原因、睡眠习惯和就医时机。'),
('NHLBI / NIH · 失眠的诊断','https://www.nhlbi.nih.gov/health/insomnia/diagnosis','慢性失眠、睡眠日记与有指征的检查。'),
('NHLBI / NIH · 失眠的治疗','https://www.nhlbi.nih.gov/health/insomnia/treatment','CBT-I、刺激控制、药物与补充剂。'),
('Mayo Clinic · 失眠的症状与原因','https://www.mayoclinic.org/diseases-conditions/insomnia/symptoms-causes/syc-20355167','身心疾病、用药和年龄相关变化。'),
('NHLBI / NIH · 睡眠呼吸暂停的症状','https://www.nhlbi.nih.gov/health/sleep-apnea/symptoms','打鼾、呼吸暂停、困倦及夜尿等线索。'),
('NINDS / NIH · 不宁腿综合征','https://www.ninds.nih.gov/health-information/disorders/restless-legs-syndrome','特征性症状、铁状态、相关疾病和肢体运动。'),
('NHS · 关于“男性更年期”','https://www.nhs.uk/conditions/male-menopause/','心理、生活方式与性腺功能减退的区别。'),
('NHLBI / NIH · 昼夜节律障碍类型','https://www.nhlbi.nih.gov/health/circadian-rhythm-disorders/types','时相延迟、轮班、时差和节律紊乱。'),
('NIMH / NIH · 双相障碍患者资料','https://www.nimh.nih.gov/health/publications/bipolar-disorder','躁狂期睡眠需要减少与其他伴随表现。'),
('Endocrine Society · 男性性腺功能减退指南','https://www.endocrine.org/clinical-practice-guidelines/testosterone-therapy','2018 年指南资源；诊断需症状与重复确认的低睾酮。'),
('AASM · 成人慢性失眠行为与心理治疗指南说明','https://aasm.org/new-guideline-supports-behavioral-psychological-treatments-for-insomnia/','2021 年指南的官方说明；推荐 CBT-I，不以睡眠卫生单独治疗。'),
('NIDDK / NIH · 甲状腺功能亢进','https://www.niddk.nih.gov/health-information/endocrine-diseases/hyperthyroidism','症状、原因与检查。'),
('NIDDK / NIH · 良性前列腺增生','https://www.niddk.nih.gov/health-information/urologic-diseases/prostate-problems/enlarged-prostate-benign-prostatic-hyperplasia','夜尿、排尿症状及需要及时就医的表现。'),
('NIDDK / NIH · 低血糖','https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/low-blood-glucose-hypoglycemia','夜间低血糖与危险信号。'),
('NHS · 泼尼松龙的副作用','https://www.nhs.uk/medicines/prednisolone/side-effects-of-prednisolone-tablets-and-liquid/','睡眠、情绪影响及不能随意停药的原因。'),
('NHS · 伪麻黄碱的副作用','https://www.nhs.uk/medicines/pseudoephedrine/side-effects-of-pseudoephedrine/','紧张、坐立不安与入睡困难。'),
('NHS · 沙丁胺醇吸入剂的副作用','https://www.nhs.uk/medicines/salbutamol-inhaler/side-effects-of-salbutamol-inhalers/','心跳加快、手抖及就医信号。'),
('NHS · 左甲状腺素','https://www.nhs.uk/medicines/levothyroxine/','剂量、失眠等副作用与药物相互作用。'),
('NHS · 抗抑郁药','https://www.nhs.uk/medicines/antidepressants/','不同药物的副作用和减停药反应。'),
('NHLBI / NIH · 睡眠呼吸暂停的原因与风险','https://www.nhlbi.nih.gov/health/sleep-apnea/causes','男性、肥胖、气道结构、酒精和相关疾病。'),
('FDA · 苯二氮䓬类用药安全警示','https://www.fda.gov/drugs/drug-safety-and-availability/fda-requiring-boxed-warning-updated-improve-safe-use-benzodiazepine-drug-class','依赖、骤停风险、逐渐减量及与酒精合用的风险。'),
('NHLBI / NIH · 心力衰竭的症状','https://www.nhlbi.nih.gov/health/heart-failure/symptoms','平卧气促、夜间气短等表现。'),
('NIDDK / NIH · 肾衰竭','https://www.niddk.nih.gov/health-information/kidney-disease/kidney-failure/what-is-kidney-failure','瘙痒、睡眠及全身症状。'),
('NIDDK / NIH · 胃食管反流的症状与原因','https://www.niddk.nih.gov/health-information/digestive-diseases/acid-reflux-ger-gerd-adults/symptoms-causes','烧心、反流与需要评估的症状。'),
('NHS · 皮肤瘙痒','https://www.nhs.uk/symptoms/itchy-skin/','皮肤和其他身体原因及处理方向。'),
('NHS · 酒精使用障碍','https://www.nhs.uk/conditions/alcohol-use-disorder/','酒精依赖、戒断与医疗支持。'),
('NIMH / NIH · 抑郁症患者资料','https://www.nimh.nih.gov/health/publications/depression','情绪、兴趣、睡眠变化和就医支持。'),
]

def esc(s):
    return html.escape(str(s), quote=True)

def refs(ids):
    assert all(1 <= i <= len(SOURCES) for i in ids)
    return ' '.join(f'<a href="#ref-{i}" aria-label="参考资料 {i}">[{i}]</a>' for i in ids)

parts = []
count = sum(len(g[3]) for g in groups)
parts.append(f'<p class="count-line"><strong>{len(groups)} 类 · {count} 项</strong> 可能因素与背景线索；编号用于查阅，不代表常见程度或风险排序。</p>')
parts.append('<nav class="catalog" aria-label="因素分类">')
for i,(slug,title,desc,items) in enumerate(groups,1):
    parts.append(f'<a href="#{slug}"><span>{i:02d}</span>{esc(title)}</a>')
parts.append('</nav><div class="scope-note"><strong>先看适用范围：</strong>这里尽可能覆盖常见、重要及容易遗漏的因素，不穷尽所有罕见病，也不意味着每个人都要做全部检查。多数因素适用于所有成年人，本页强调中年男性更值得留意的组合。每项的“识别线索”用于与医生讨论，不是诊断标准。治疗方向是基于资料的科普整理，不是个人处方。</div>')
parts.append('<div class="legend" aria-label="关联类型说明"><span class="tag">可影响入睡</span><span class="tag maintain">多见夜间醒来</span><span class="tag background">背景 / 间接因素</span><span>标签只表示主要关联，可以重叠。</span></div>')
tags={'onset':('可影响入睡',''),'maintain':('多见夜间醒来','maintain'),'background':('背景 / 间接因素','background')}
n=0
for i,(slug,title,desc,items) in enumerate(groups,1):
    parts.append(f'<article class="factor-group" id="{slug}" aria-labelledby="heading-{slug}"><div class="group-heading"><span class="group-num">{i:02d}</span><h3 id="heading-{slug}">{esc(title)}</h3></div><p class="group-desc">{esc(desc)}</p>')
    for title,kind,mechanism,clues,action,boundary,ids in items:
        n+=1
        label,css=tags[kind]
        if title.startswith('酒精助眠'):
            ids=[2,4,21,27]
        open_attr=' open' if n==1 else ''
        parts.append(f'<details id="factor-{n}"{open_attr}><summary><span class="factor-title"><span class="factor-no">{n:02d}</span>{esc(title)}</span><span class="tag {css}">{label}</span></summary><div class="factor-body">')
        for term,value in [('如何影响',mechanism),('识别线索',clues),('下一步',action)]:
            parts.append(f'<p><strong>{term}：</strong>{esc(value)}</p>')
        parts.append(f'<p class="context"><strong>不要忽略：</strong>{esc(boundary)}</p><p class="refs">相关资料 {refs(ids)}</p></div></details>')
    parts.append('</article>')

next_section='''<section id="next" class="content"><p class="eyebrow">从这里开始</p><h2>先找规律，再做有针对性的改变。</h2><p>不需要一次检查所有原因。把睡眠的变化、白天状态和伴随症状联系起来，通常比反复计算昨晚睡了几小时更有用。</p><div class="steps">
<article class="step"><h3><span>01</span>记录 1–2 周</h3><p>每天晨起后回忆记录，不需要夜里盯表。</p><ul><li>上床时间、估计入睡所需时间、夜间醒来、最终醒来与起床时间。</li><li>午睡、咖啡因、烟酒、运动、药物及补充剂的时间。</li><li>白天困倦、情绪、疼痛、反流、腿部不适、夜尿和伴侣观察到的打鼾憋气。</li></ul><p class="small">睡眠日记是沟通工具，不是要求精确到每分钟。<a href="#ref-3">[3]</a></p></article>
<article class="step"><h3><span>02</span>先处理最相关的一两项</h3><p>例如稳定起床、把咖啡因提前停止、移走睡前工作或改善卧室。困了再上床，白天保持适当活动；留出充足睡眠机会。</p><p>若上床后明显清醒且烦躁，可起身到安全、光线较暗的地方安静活动，困了再回床。不要一边看时间，一边强迫自己睡着。</p><p class="small">有明显嗜睡时不要驾驶或操作危险设备。<a href="#ref-2">[2]</a> <a href="#ref-4">[4]</a></p></article>
<article class="step"><h3><span>03</span>带线索就诊，检查按需选择</h3><p>可先找全科、睡眠门诊；打鼾憋醒可看呼吸科，腿部症状可看神经科，持续情绪问题可看精神心理科。</p><p>医生可能根据线索安排甲状腺、血糖、铁状态或睡眠呼吸检查。普通失眠并非人人都需要睡眠监测、脑影像或一整套激素检查。</p><p class="small">就诊时携带完整药物清单及既往检查。<a href="#ref-3">[3]</a> <a href="#ref-7">[7]</a> <a href="#ref-11">[11]</a></p></article>
<article class="step"><h3><span>04</span>避免“越补越乱”</h3><p>不要自行靠酒精助眠，不要叠加安眠药，也不要突然停掉长期用药。褪黑素更需要考虑适应情形与时机，不能把所有失眠当成“缺褪黑素”。</p><p>非处方抗过敏助眠药和保健品也有风险。怀疑缺铁或睾酮不足时先评估，不根据失眠自行补充。</p><p class="small">药物的取舍由医生结合获益、风险与共病决定。<a href="#ref-4">[4]</a> <a href="#ref-7">[7]</a> <a href="#ref-11">[11]</a> <a href="#ref-22">[22]</a></p></article></div>
<aside class="treatment"><h3>长期失眠，重点了解 CBT-I。</h3><p>失眠认知行为治疗（CBT-I）通常是成人慢性失眠的首选治疗，结合认知调整、刺激控制、睡眠安排和放松训练等方法。它比一张“睡前注意事项”清单更系统；仅靠睡眠卫生建议通常不足以治疗慢性失眠。</p><p>睡眠限制或压缩卧床时间属于专业治疗内容，不建议照着网上时间表自行大幅减少睡眠。合并双相障碍、癫痫、危险困倦等情况，应先做适合性评估。伴随疾病也需要同步处理。</p><p class="small">依据 NHLBI 治疗资料和 AASM 行为治疗指南说明。<a href="#ref-4">[4]</a> <a href="#ref-12">[12]</a></p></aside></section>'''
care_section='''<section id="care" class="content care"><p class="eyebrow">就医时机</p><h2>影响了白天，就值得寻求帮助。</h2><div class="scope-note"><strong>慢性失眠的常用判断：</strong>在有足够睡眠机会和适宜环境的情况下，入睡或维持睡眠困难等问题每周至少 3 晚、持续至少 3 个月，并伴日间功能受损。这个标准用于临床评估，<strong>不是要求等满三个月才就医</strong>。偶尔超过 30 分钟才入睡，也不能单独用来诊断。<a href="#ref-3">[3]</a> <a href="#ref-12">[12]</a></div>
<div class="care-grid"><article class="care-box"><h3>安排门诊，或尽快评估</h3><ul><li>持续数周或反复发生，调整习惯后仍没有改善；白天明显疲倦、注意力下降或情绪受到影响。</li><li>响亮打鼾、目击呼吸暂停、憋醒，或白天困到容易打盹；发生困倦驾驶时先停止驾驶。</li><li>夜间腿部活动冲动、明显疼痛、反流、频繁夜尿，或新用药后睡眠显著改变。</li><li>明显抑郁、持续焦虑，或几天睡很少却异常亢奋、冲动，应尽快评估精神状态。</li></ul><p class="small"><a href="#ref-2">[2]</a> <a href="#ref-6">[6]</a> <a href="#ref-7">[7]</a> <a href="#ref-10">[10]</a></p></article>
<article class="care-box urgent"><h3>出现这些情况，立即求助</h3><ul><li>胸痛、严重呼吸困难、晕厥、意识异常、抽搐等急性症状。</li><li>有自伤或自杀想法、计划，或无法确保自己安全；严重躁动、幻觉、妄想或危险行为。</li><li>减停酒精或镇静药后出现明显戒断，特别是幻觉、抽搐或意识改变。</li></ul><p><strong>在中国大陆可拨打 120，或到最近急诊；其他地区使用当地急救电话。</strong>精神危机时尽量让可信任的人陪伴，避免独自驾车前往。</p><p class="small">急症需要即时评估，不能作为普通失眠在家等待。<a href="#ref-10">[10]</a> <a href="#ref-15">[15]</a> <a href="#ref-22">[22]</a> <a href="#ref-23">[23]</a> <a href="#ref-27">[27]</a></p></article></div></section>'''
source_items=''.join(f'<li id="ref-{i}"><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(title)} ↗</a><p>{esc(desc)}</p></li>' for i,(title,url,desc) in enumerate(SOURCES,1))
source_section=f'''<section id="sources" class="content"><p class="eyebrow">参考资料 · {len(SOURCES)} 个公开来源</p><h2>有依据，也说明边界。</h2><p>资料查阅日期：2026 年 9 月 26 日。正文为中文科普整理，非原文逐字翻译；识别线索与处理方向是结合公开资料作的说明，不代表确定因果关系或个体诊断。各来源的发布、更新日期不同，查阅日期不等于指南更新日期。</p><p class="small">本页未经过针对个人的问诊或专业临床审查，不能替代诊疗。若症状、药物或指南有变化，以专业人员的最新评估为准。页面不收集个人健康信息，没有账户、统计追踪或外部脚本。</p><ol id="source-list">{source_items}</ol></section>'''

doc=(ROOT/'src/template.html').read_text()
doc=re.sub(r'<div id="factor-content">.*?</div></section>', '<div id="factor-content">'+''.join(parts)+'</div></section>', doc, count=1, flags=re.S)
doc=re.sub(r'<section id="next".*?</section>',next_section,doc,count=1,flags=re.S)
doc=re.sub(r'<section id="care".*?</section>',care_section,doc,count=1,flags=re.S)
doc=re.sub(r'<section id="sources".*?</section>',source_section,doc,count=1,flags=re.S)
# Native details remain readable without JavaScript. For browser printing, temporarily open all.
doc=doc.replace('</body>','''<script>
(() => { let previous; window.addEventListener('beforeprint', () => { previous = [...document.querySelectorAll('details')].map(d => [d, d.open]); previous.forEach(([d]) => d.open = true); }); window.addEventListener('afterprint', () => { if (previous) previous.forEach(([d, wasOpen]) => d.open = wasOpen); }); })();
</script></body>''')
assert doc.count('<details ')==count
ids=set(re.findall(r' id="([^"]+)"',doc))
assert all(x in ids for x in re.findall(r'href="#([^"]+)"',doc)), 'Broken internal anchor'
assert len(re.findall(r' id="([^"]+)"',doc))==len(ids), 'Duplicate ID'
(ROOT/'index.html').write_text(doc)
print(f'Built {count} factors, {len(groups)} categories, {len(SOURCES)} sources; all internal anchors valid.')
