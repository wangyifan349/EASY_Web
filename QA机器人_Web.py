from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
CORS(app)
model = SentenceTransformer('all-mpnet-base-v2')


def edit_distance(s1, s2):
    """
    计算字符串 s1 和 s2 之间的编辑距离
    使用动态规划方法实现
    """
    m, n = len(s1), len(s2)
    # 初始化 dp 数组，dp[i][j] 表示 s1[0:i] 和 s2[0:j] 的编辑距离
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    # 初始情况：编辑任意一个空串到另一个串需要插入所有字符
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    # 填充 dp 表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # 没有操作
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,    # 删除
                    dp[i][j - 1] + 1,    # 插入
                    dp[i - 1][j - 1] + 1 # 替换
                )
    return dp[m][n]


def longest_common_subsequence(s1, s2):
    """
    计算字符串 s1 和 s2 的最长公共子序列（LCS）
    返回 LCS 的长度和具体子序列
    """
    m, n = len(s1), len(s2)
    # dp[i][j] 表示 s1[0:i] 和 s2[0:j] 的最长公共子序列长度
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    # 计算 dp 数组
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # 反向构造 LCS 序列
    i, j = m, n
    lcs_seq = []
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            lcs_seq.append(s1[i - 1])
            i -= 1
            j -= 1
        else:
            if dp[i - 1][j] >= dp[i][j - 1]:
                i -= 1
            else:
                j -= 1
    lcs_seq.reverse()  # 因为是从后往前添加的
    return dp[m][n], ''.join(lcs_seq)
"""
str1 = "intention"
str2 = "execution"
print("编辑距离示例:")
distance = edit_distance(str1, str2)
print("字符串 '%s' 和 '%s' 的编辑距离为: %d" % (str1, str2, distance))
print("\n最长公共子序列示例:")
s1 = "AGGTAB"
s2 = "GXTXAYB"
lcs_length, lcs = longest_common_subsequence(s1, s2)
print("字符串 '%s' 和 '%s' 的最长公共子序列长度为: %d" % (s1, s2, lcs_length))
print("最长公共子序列: %s" % lcs)
"""
"""
import math
def l2_distance(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("两个向量的维度必须相同")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(vec1, vec2)))
def cosine_similarity(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("两个向量的维度必须相同")
    dot_product = sum(x * y for x, y in zip(vec1, vec2))
    norm1 = math.sqrt(sum(x ** 2 for x in vec1))
    norm2 = math.sqrt(sum(x ** 2 for x in vec2))
    if norm1 == 0 or norm2 == 0:
        raise ValueError("向量中存在零向量，无法计算余弦相似度")
    return dot_product / (norm1 * norm2)
"""



qa_dict = {
    "阿莫西林是什么？": (
        "阿莫西林是一种青霉素类抗生素，主要通过干扰细菌细胞壁的合成杀灭细菌。"
        "\n【作用原理】："
        "\n  - 阿莫西林分子中含有β-内酰胺环，该结构与细菌细胞壁合成必需的青霉素结合蛋白（PBP）发生可逆性结合。"
        "\n  - PBP在细菌内催化肽聚糖分子交联过程，形成坚固的细胞壁结构。阿莫西林结合后，"
        "\n    阻断了这一交联过程，使得肽聚糖的架构无法正常构建。"
        "\n  - 随着细胞生长和分裂，未能形成完整的细胞壁导致细胞在高渗透压环境下最终破裂死亡。"
        "\n【深层机理】："
        "\n  - 分子层面来看，β-内酰胺环与PBP的活性位点中的丝氨酸残基发生共价键结合，仿佛“伪底物”，使得PBP失去催化功能。"
        "\n  - 此外，阿莫西林对多种PBP具有一定亲和力，能够抑制多种细菌中多个关键酶的活性，从而发挥广谱抗菌作用。"
        "\n【应用】：常用于治疗呼吸道、耳鼻喉、皮肤软组织及部分尿路感染。"
    ),
    "抗病毒药物有哪些用途？": (
        "抗病毒药物用于干扰病毒在宿主细胞内的生命周期，针对不同病毒具备不同的作用靶点。"
        "\n【作用原理】："
        "\n  - 阻断病毒与宿主细胞的结合：部分抗病毒药能与宿主细胞表面的受体或病毒衣壳蛋白结合，"
        "\n    防止病毒进入细胞。例如部分流感病毒药物可干扰病毒中血凝素（HA）与宿主受体的亲和性。"
        "\n  - 抑制病毒核酸复制：许多药物（如核苷类似物）在细胞内被激活，"
        "\n    以“错误底物”插入病毒DNA或RNA链中，导致链终止，例如阿昔洛韦在疱疹病毒中的应用。"
        "\n  - 抑制病毒蛋白加工或装配：一些药物能够干扰病毒蛋白酶的活性，"
        "\n    阻止前体蛋白的切割和成熟，从而阻断新病毒颗粒的有效组装。"
        "\n【深层机理】："
        "\n  - 分子水平上，核苷类似物与正常核苷结构相似，经细胞激酶磷酸化后掺入病毒核酸聚合酶催化的新生链中，"
        "\n    导致后续碱基无法继续添加，形成链终止。"
        "\n  - 对于蛋白酶抑制剂，如HIV蛋白酶抑制剂，其分子结构设计往往模拟底物的关键结构部分，"
        "\n    与蛋白酶活性位点结合，竞争性地抑制酶的功能，防止前蛋白正确剪切。"
        "\n【应用】：主要用于治疗流感、疱疹、HIV、病毒性肝炎等不同类型的病毒感染。"
    ),
    "什么是布洛芬？": (
        "布洛芬是一种非甾体抗炎药（NSAID），在临床上用于缓解疼痛、发热和炎症。"
        "\n【作用原理】："
        "\n  - 布洛芬通过非选择性抑制体内环氧化酶（COX-1和COX-2）的活性，使得前列腺素（尤其是PGE2）的合成减少。"
        "\n  - 前列腺素在疼痛、发炎和发热过程中作为信号分子，负责介导发炎介质的释放及神经信号传递。"
        "\n  - 抑制这一途径直接削弱了炎症反应和痛觉传导，同时干扰下丘脑中的温度调控中枢，从而达到退热效果。"
        "\n【深层机理】："
        "\n  - 在分子层面，布洛芬与COX酶的疏水性口袋结合，阻止花生四烯酸进入活性位点，从而抑制后续的氧化反应。"
        "\n  - 这种抑制作用既影响炎症介质合成，也降低了因炎症引起的免疫反应信号传递。"
        "\n【应用】：用于缓解各种轻中度疼痛（如头痛、牙痛、关节痛）以及降低发热。"
    ),
    "什么是青霉素？": (
        "青霉素是一类典型的β-内酰胺抗生素，以其特有的β-内酰胺环为结构基础，对细菌细胞壁具有强大的抑制作用。"
        "\n【作用原理】："
        "\n  - 青霉素能与细菌细胞壁合成过程中的青霉素结合蛋白（PBP）结合，干扰肽聚糖分子交联。"
        "\n  - 这种交联是生成坚固细菌细胞壁的关键步骤。失去了交联作用，细胞壁将逐渐变软，失去抵抗内外渗透压的能力。"
        "\n  - 在渗透压作用下，细菌细胞内水分进入，使细胞膜破裂，导致细菌死亡。"
        "\n【深层机理】："
        "\n  - 从结构生物学角度，青霉素分子的β-内酰胺环与PBP的活性位点特异性结合，其化学结构模仿了肽聚糖前体的部分结构。"
        "\n  - 此种模拟使得PBP错误识别并结合青霉素而非正常底物，从而导致其催化活性丧失。"
        "\n【应用】：主要用于对抗敏感菌感染，特别是针对革兰氏阳性菌（如链球菌）具有广谱杀菌作用。"
    ),
    "什么是降压药？": (
        "降压药是一类用于调控血压的药物，通过不同的生理和分子机制降低心血管系统的压力。"
        "\n【作用原理】："
        "\n  - 利尿剂：利用调节肾小管对钠及水分的重吸收，减少血容量；从分子层面上，调控相应转运蛋白的活性。"
        "\n  - β-受体阻滞剂：通过竞争性抑制交感神经释放的去甲肾上腺素与心脏β受体的结合，降低心率及心肌收缩力，"
        "\n    减少心脏输出。"
        "\n  - 钙通道阻滞剂：抑制电压依赖性钙通道，减少钙离子进入平滑肌细胞，降低肌肉细胞内钙信号，从而使血管平滑肌松弛。"
        "\n  - ACEI/ARBs：ACEI通过抑制血管紧张素转换酶（ACE）活性降低血管紧张素II的生成，而ARBs则直接阻断血管紧张素II与其受体结合，"
        "\n    这两者都减少了血管平滑肌细胞内信号通路的激活，进一步引起血管扩张。"
        "\n【深层机理】："
        "\n  - 例如在使用ACEI时，血管紧张素I无法转换为具有强烈血管收缩作用的血管紧张素II，"
        "\n    同时上调缓激肽（一种天然血管舒张剂）的水平，进一步增强降压效果。"
        "\n  - 钙通道阻滞剂在分子层面上通过抑制钙通道α1亚单位，减少了钙依赖性信号转导，降低细胞内钙浓度。"
        "\n【应用】：根据个体差异和病理生理状态，临床上可选择单药或联合使用降压药以实现有效血压控制。"
    ),
    "抗生素的滥用会有什么后果？": (
        "抗生素滥用从分子和微生物生态学角度均带来深远影响。"
        "\n【深层机理】："
        "\n  - 高频率或不恰当使用抗生素会在细菌种群中施加持续选择压力，诱导细菌发生基因突变以及水平转移耐药基因（如质粒、整合子等）的积累。"
        "\n  - 这种基因水平扩散使得耐药菌迅速传播，最终导致常规抗生素失去有效杀菌作用。"
        "\n  - 同时，抗生素在广谱杀菌过程中扰乱了宿主体内正常菌群的微生态平衡，为耐药菌和机会性病原菌的扩增提供空间。"
        "\n【结果】：导致后续治疗难度和复杂性增加，同时给公共卫生带来严峻挑战。"
    ),
    # 可根据需求继续扩展其他条目
}
questions = list(qa_dict.keys())
question_embeddings = model.encode(questions, convert_to_tensor=True)

def find_most_similar_question(query):
    query_embedding = model.encode(query, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(query_embedding, question_embeddings).squeeze(0)
    max_index = cosine_scores.argmax().item()
    question = questions[max_index]
    answer = qa_dict[question]
    score = cosine_scores[max_index].item()
    return {'question': question, 'answer': answer, 'score': score}

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    query = data.get('query', '')
    result = find_most_similar_question(query)
    return jsonify(result)

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <title>医学问答系统</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f8f9fa;
            }

            .chat-container {
                width: 400px;
                max-width: 100%;
                height: 600px;
                display: flex;
                flex-direction: column;
                border: 1px solid #ccc;
                background-color: white;
                border-radius: 10px;
                overflow: hidden;
            }

            .chat-messages {
                flex: 1;
                padding: 15px;
                overflow-y: scroll;
                background-color: #e9ecef;
            }

            .message-box {
                margin: 5px 0;
                padding: 10px;
                border-radius: 10px;
            }

            .user-message {
                background-color: #d4edda;
                text-align: right;
            }

            .answer-message {
                background-color: #f1f8ff;
                text-align: left;
            }

            .chat-input {
                padding: 10px;
                border-top: 1px solid #ccc;
                display: flex;
            }

            .chat-input input {
                flex: 1;
                padding: 10px;
                border-radius: 20px;
                border: 1px solid #ccc;
                outline: none;
            }
            .chat-input button {
                margin-left: 10px;
                padding: 10px 20px;
                border-radius: 20px;
                border: none;
                background-color: #28a745;
                color: white;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-input">
            <input type="text" id="question" placeholder="输入您的问题">
            <button onclick="askQuestion()">发送</button>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function appendMessage(message, type) {
            const messageBox = $('<div></div>').addClass('message-box').addClass(type);
            messageBox.text(message);
            $('#chatMessages').append(messageBox);
            $('#chatMessages').scrollTop($('#chatMessages')[0].scrollHeight);
        }

        function askQuestion() {
            const questionInput = $('#question');
            const question = questionInput.val();

            if (question.trim() === '') return;

            appendMessage(question, 'user-message');
            questionInput.val('');

            $.ajax({
                url: '/ask',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ query: question }),
                success: function (response) {
                    appendMessage(response.answer, 'answer-message');
                },
                error: function (error) {
                    appendMessage('出现错误，请重试。', 'answer-message');
                    console.error('Error:', error);
                }
            });
        }
    </script>

    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=False)
