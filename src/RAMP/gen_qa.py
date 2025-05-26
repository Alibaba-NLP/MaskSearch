import json
import os
import random
from model import call_with_messages
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from hanziconv import HanziConv

query_prompt_zh = """{paragraph}

补充所有的[mask]，并重新输出，要求格式不能发生变化。"""

query_prompt_en = """{paragraph}

Fill in all the [mask] and output the whole paragraph without changing its format."""

ner_prompt_zh = """
从以下文本中提取所有知识实体（最好5个以上），知识实体是指文本中提到的全部具体中文人物、地点、组织、会议期刊、短学术名词概念，以及唯一出现的短数字等。如果多个实体连续出现，只提取最细粒度的实体。重复出现的实体不要提取。
请将提取的实体以列表的形式直接输出，无需输出其他内容。每个实体不要超过10个字。
确保你提取的实体不能通过该段落中的上下文直接推理出来，需要额外的信息搜索才能推理。
你的实体只能是中文或者数字。

##例子
段落：1980年2月27日，林义雄妻子方素敏前往军事情报局看守所并且代替国际特赦组织大坂市办事处传达讯息。而隔天军事法庭召开第一次调查庭，包括方素敏等待审党外运动人士的家属纷纷前往看守所探视和旁听。不过方素敏则对于家中小孩感到不放心，担任林义雄议员秘书的田秋堇则搭乘公车先行前往林义雄在台北市信义住家。发现林义雄9岁的长女林奂均身中6刀重伤后田秋堇赶紧向外求助，之后林浊水和康文雄等党外运动人士在接到消息赶来帮忙后，在住处地下室分别发现其中身中14刀的林义雄母亲林游阿­妹，以及各自因为从后背贯穿前胸的1刀丧命的双胞胎女儿林亮均与林亭均。
实体：["方素敏", "国际特赦组织大坂市办事处", "台北市信义", "6", "14", "林奂均", "林浊水", "康文雄", "林游阿­妹", "林亮均", "林亭均"]

段落：近日，上海科技大学信息科学与技术学院后摩尔中心（PMICC）寇煦丰、祝智峰团队，利用分子束外延技术设计制备了基于2英寸磁性拓扑异质结Bi2Te3/CrTe2薄膜，实现了能同时具备类脑突触和神经元功能的自旋轨道矩器件阵列（spin-orbit torque device array），并集成了批量归一化算法和可训练激活函数，相关研究成果以"Integrated Artificial Neural Network with Trainable Activation Function Enabled byTopological Insulator-based Spin-Orbit Torque Devices"为题在线发表于知名学术期刊ACS Nano。
实体：["上海科技大学", "寇煦丰", "祝智峰", "自旋轨道矩器件阵列", "ACS Nano"]

段落：对于开放定址法，荷载因子是特别重要因素，应严格限制在0.7-0.8以下。超过0.8，查表时的CPU缓存不命中（cache missing）按照指数曲线上升。因此，一些采用开放定址法的hash库，如Java的hash库限制了荷载因子为0.75，超过此值将resize散列表。
实体：["荷载因子", "指数曲线", "Java", "散列表", "0.75"]

段落：大连公交车以12米为主，目前最小为6米级。纯电动逐渐占据主导地位。目前的主力车型是比亚迪K9系列纯电动客车，目前大连公交开始大批量采购比亚迪纯电动客车。柴油、天然气及混合动力车辆逐渐退出大连公交的舞台。
实体：["比亚迪K9", "6", "12"]

段落：{paragraph}
实体：
"""

ner_prompt_en = """
Extract all the knowledge entities (more than 5 entities if exist) from the following text. Knowledge entities refer to specific individuals, locations, organizations, conferences, journals, short academic concepts, and unique short numbers mentioned in the text. If multiple entities appear consecutively, only extract the finest-grained entity. Please output the extracted entities as a list directly, without any other content. Each entity should not exceed 10 characters.
If an entity repeatedly appears, you should not extract it. You need extract a whole word like [American] instead of [America]n.
Ensure that the entities you extract cannot be directly infer from the context of the paragraph. You must need extra information search on the Internet to infer the entities.

##Example
Paragraph: On February 27, 1980, Lin Yixiong's wife, Fang Sumin, went to the military intelligence bureau detention center and conveyed messages on behalf of the International Amnesty Organization Osaka office. The next day, the military court held its first investigation session, and families waiting for the trial of opposition movement activists, including Fang Sumin, went to the detention center to visit and listen. However, Fang Sumin was worried about her children at home, and Tian Qiujin, who served as Lin Yixiong's secretary, took the bus to Lin Yixiong's residence in Xinyi, Taipei City. Upon discovering that Lin Yixiong's 9-year-old eldest daughter, Lin Huanjun, was seriously injured with six stab wounds, Tian Qiujin quickly sought help. Subsequently, Lin Zhuoshui and Kang Wenxiong, among other opposition movement activists, rushed to help after receiving the news and found Lin Yixiong's mother, Lin You'a, stabbed 14 times, and her twin daughters, Lin Liangjun and Lin Tingjun, who died from a single stab wound that pierced their backs and exited their chests, in the basement of the residence.
Entities: ["Lin Yixiong", "Fang Sumin", "International Amnesty Organization Osaka office", "Tian Qiujin", "Xinyi, Taipei City", "6", "14", "Lin Huanjun", "Lin Zhuoshui", "Kang Wenxiong", "Lin You'a", "Lin Liangjun", "Lin Tingjun"]

Paragraph: Recently, the team of Kou Xufen and Zhu Zhifeng from the Post-Moore Center (PMICC) at the School of Information Science and Technology, ShanghaiTech University, designed and prepared a 2-inch magnetic topological heterojunction Bi2Te3/CrTe2 thin film based on molecular beam epitaxy technology. They achieved a spin-orbit torque device array capable of possessing both brain-like synapse and neuron functions, and integrated batch normalization algorithms and trainable activation functions. The relevant research results were published online in the renowned academic journal ACS Nano under the title "Integrated Artificial Neural Network with Trainable Activation Function Enabled by Topological Insulator-based Spin-Orbit Torque Devices".
Entities: ["ShanghaiTech University", "Kou Xufen", "Zhu Zhifeng", "spin-orbit torque device array", "ACS Nano"]

Paragraph: For open addressing, the load factor is a particularly important factor and should be strictly limited below 0.7-0.8. Beyond 0.8, CPU cache misses (cache missing) increase exponentially when looking up tables. Therefore, some hash libraries that use open addressing, such as Java's hash libraries, limit the load factor to 0.75, and the hash table will be resized when this value is exceeded.
Entities: ["load factor", "exponential curve", "Java", "hash table", "0.75"]

Paragraph: Dalian buses are mainly 12 meters long, with the smallest currently being 6 meters. Pure electric vehicles are gradually taking the dominant position. The main model is the BYD K9 series pure electric bus, and Dalian public transportation has begun to purchase a large number of BYD pure electric buses. Diesel, natural gas, and hybrid vehicles are gradually exiting the stage of Dalian public transportation.
Entities: ["BYD K9", "6", "12"]

Paragraph: {paragraph}
Entities:
"""


def ner(para, args):
    if 'zh' in args.corpus:
        prompt = ner_prompt_zh.format(paragraph=para)
    else:
        prompt = ner_prompt_en.format(paragraph=para)

    prompt = [{'role': 'system', 'content': 'You are a helpful assistant.'}, 
            {'role': 'user', 'content': prompt}]
    response = call_with_messages(args.model, prompt)
    response = eval(response)
    return response

def generate_qa(paragraph, args):
    try:
        if "zh" in args.corpus:
            para, title = paragraph[0], HanziConv.toSimplified(paragraph[1])
        else:
            para, title = paragraph[0], paragraph[1]
        entities = ner(para, args)
    except:
        print("NER error")
        return []

    if title in entities:
        entities.remove(title)

    for e in entities:
        if para.count(e) > 1:
            entities.remove(e)
    if len(entities) == 0:
        return []
    pairs = []
    for _ in range(1):
        if len(entities) < 3:   # 1, 2
            num_mask = random.randint(min(len(entities), 1), min(len(entities), 4))
            # num_mask = 1
        elif len(entities) >= 4: # 4, 5, ...
            num_mask = 4
        else:   # 3
            num_mask = random.randint(3, min(len(entities), 4))

        def get_weight(entity, is_zh, is_num=False, max_weight=0):
            if is_num:
                return max_weight
            if is_zh:
                return len(entity)
            else:
                return len(entity.split(" "))

        non_numeric_entities = [entity for entity in entities if not entity.isdigit()]
        max_weight = max(get_weight(entity, "zh" in args.corpus) for entity in non_numeric_entities) if non_numeric_entities else 1
        weights = [get_weight(entity, "zh" in args.corpus, entity.isdigit(), max_weight) for entity in entities]
        sampled_indexes = random.choices(range(len(entities)), weights=weights, k=num_mask)
        masks = [entities[i] for i in sorted(sampled_indexes)]
            
        if title.split(' (')[0] not in para:
            para = para.replace("他们", title.split(' (')[0], 1).replace("她", title.split(' (')[0], 1).replace("他", title.split(' (')[0], 1).replace("它", title.split(' (')[0], 1)
        if title.split(' (')[0] not in para:
            para = title.split(' (')[0] + " " + para
        masked_paragraph = para
        for m in masks:
            masked_paragraph = masked_paragraph.replace(m, '[mask]', 1)

        if masked_paragraph.startswith('[mask]'):
            continue

        if "zh" in args.corpus:
            pairs.append({"query": query_prompt_zh.format(paragraph=masked_paragraph), "answer": para, "ext": {"mask_num": num_mask, "masks": masks, "entities": entities, "source": "wiki", "title": title}})
        else:
            pairs.append({"query": query_prompt_en.format(paragraph=masked_paragraph), "answer": para, "ext": {"mask_num": num_mask, "masks": masks, "entities": entities, "source": "wiki", "title": title}})
    return pairs
    

def process_file(fp, existing_title):
    if fp in existing_title:
        return []
    if 'zh' in args.corpus:
        with open(f'{args.corpus}/{fp}', 'r') as f:
            content = f.read().split('\n')
            para = [c for c in content if '图表' not in c and c.count('/') < 2 and not c.startswith('*') and not c.endswith("：")] # Filter Pages
            if len(para) > 2:
                return [(p, fp) for p in random.sample(para, len(para) - 1)]
            elif len(para) == 2:
                return [(p, fp) for p in random.sample(para, 2)]
            elif len(para) == 1:
                return [(para[0], fp)]
            return []
    else:
        with open(f'{args.corpus}/{fp}', 'r') as f:
            content = f.read().split('\n')
            para = [c for c in content if 'List' not in c and c.count('/') < 2 and not c.startswith('*') and not c.endswith("：")]    # Filter Pages
            if len(para) > 2:
                return [(p, fp) for p in random.sample(para, len(para))]
            elif len(para) == 2:
                return [(p, fp) for p in random.sample(para, 2)]
            elif len(para) == 1:
                return [(para[0], fp)]
            return []

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument('--num_threads', type=int, default=250)
    argparse.add_argument('--model', type=str, default='qwen-turbo')

    argparse.add_argument('--corpus', type=str, default='wiki-en', help='Directory of Wiki Pages')
    argparse.add_argument('--output_path', type=str, default='qa_en.jsonl')
    argparse.add_argument('--continue_gen', action_store=True)

    args = argparse.parse_args()

    files = os.listdir(args.corpus)
    random.seed(42)
    random.shuffle(files)

    existing_title = set()
    if args.continue_gen:
        with open(args.output_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f):
                data = json.loads(line)
                existing_title.add(data["ext"]["title"])
        
    paragraphs = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_file = {executor.submit(process_file, fp, existing_title): fp for fp in files}
        for future in tqdm(as_completed(future_to_file), total=len(files), desc='Processing files'):
            try:
                paragraphs.extend(future.result())
            except:
                pass

    with open(args.output_path, 'a') as f:
        with ThreadPoolExecutor(max_workers=args.num_threads) as executor:
            results = {executor.submit(generate_qa, item, args): item for item in paragraphs}
            
            for future in tqdm(as_completed(results),total=len(paragraphs)):
                item = results[future]
                try:
                    data = future.result()
                    for d in data:
                        f.write(json.dumps(d, ensure_ascii= False) +'\n')
                        f.flush()
                
                except Exception as e:
                    print(f'error in thread:{item}, {e}')
                    