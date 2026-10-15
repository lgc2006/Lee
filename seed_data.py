import httpx

BASE = 'http://127.0.0.1:8000'

# login
r = httpx.post(f'{BASE}/api/admin/login', json={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

competitions = [
    {
        'title': '2026年全国大学生数学建模竞赛',
        'category': '学科竞赛',
        'description': '<h2>赛事介绍</h2><p>全国大学生数学建模竞赛创办于1992年，每年一届，是首批列入"高校学科竞赛排行榜"的19项竞赛之一。</p><p>竞赛宗旨：创新意识、团队精神、重在参与、公平竞争。</p><h2>竞赛形式</h2><p>三名大学生组成一队，在3天时间内，就指定的问题完成从建立模型、求解、验证到论文撰写的全部工作。</p>',
        'requirements': '<h2>参赛对象</h2><ul><li>全国普通高等学校全日制在校本科生</li><li>三人一组，可跨专业组队</li></ul><h2>报名条件</h2><ul><li>具备一定的数学基础和编程能力</li><li>具有较强的论文写作能力</li></ul>',
        'registration_method': '以学校为单位统一组织报名，请联系指导教师。',
        'registration_url': 'https://mcm.edu.cn',
        'registration_deadline': '2026-09-05T23:59:59',
        'competition_date': '2026-09-15T08:00:00',
        'organizer': '中国工业与应用数学学会',
        'contact_person': '张老师',
        'contact_phone': '13800138001',
    },
    {
        'title': '第十届"互联网+"大学生创新创业大赛',
        'category': '创新创业',
        'description': '<h2>赛事介绍</h2><p>中国"互联网+"大学生创新创业大赛由教育部主办，是国内规格最高的大学生创新创业赛事之一。</p><p>大赛旨在深化高等教育综合改革，激发大学生的创造力，培养造就"大众创业、万众创新"的主力军。</p>',
        'requirements': '<h2>参赛对象</h2><ul><li>普通高等学校全日制在校生</li><li>毕业5年以内的毕业生</li></ul><h2>项目要求</h2><ul><li>具备创新性和可行性</li><li>有清晰商业模式</li></ul>',
        'registration_method': '登录大赛官网在线报名，提交项目计划书。',
        'registration_url': 'https://cy.ncss.cn',
        'registration_deadline': '2026-10-31T23:59:59',
        'competition_date': '2026-12-01T08:00:00',
        'organizer': '教育部',
        'contact_person': '李老师',
        'contact_phone': '13800138002',
    },
    {
        'title': '校园歌手大赛',
        'category': '文体活动',
        'description': '<h2>赛事介绍</h2><p>一年一度的校园歌手大赛即将拉开帷幕！这是展示你音乐才华的最佳舞台。</p><p>本届比赛设有独唱、合唱两个组别，获奖选手将获得丰厚的奖品和荣誉证书。</p>',
        'requirements': '<h2>参赛对象</h2><ul><li>全体在校学生</li></ul><h2>参赛要求</h2><ul><li>歌曲内容健康向上</li><li>时长不超过5分钟</li></ul>',
        'registration_method': '扫码填写报名表，或到学生会办公室现场报名。',
        'registration_deadline': '2026-08-20T23:59:59',
        'competition_date': '2026-09-10T18:00:00',
        'organizer': '校团委学生会',
        'contact_person': '万同学',
        'contact_phone': '13900139001',
    },
    {
        'title': '暑期社会实践项目评选',
        'category': '社会实践',
        'description': '<h2>活动介绍</h2><p>暑期社会实践是大学生走向社会、了解国情的重要途径。本年度评选将表彰在暑期社会实践中表现突出的团队和个人。</p>',
        'requirements': '<h2>参评条件</h2><ul><li>暑期社会实践团队成员</li><li>提交完整的实践报告</li></ul>',
        'registration_method': '提交纸质材料至各学院分团委。',
        'registration_deadline': '2026-07-31T23:59:59',
        'competition_date': '2026-09-20T14:00:00',
        'organizer': '校团委实践部',
        'contact_person': '王老师',
        'contact_phone': '13800138003',
    },
]

for i, c in enumerate(competitions):
    r = httpx.post(f'{BASE}/api/competitions/', json=c, headers=headers)
    comp_id = r.json()['id']
    httpx.post(f'{BASE}/api/competitions/{comp_id}/submit', headers=headers)
    httpx.post(f'{BASE}/api/competitions/{comp_id}/audit', json={'action':'approve'}, headers=headers)
    print(f'[{i+1}/4] {c["title"]} - published (id={comp_id})')

print('\nAll seed data created.')
