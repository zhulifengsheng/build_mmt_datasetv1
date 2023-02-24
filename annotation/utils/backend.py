import os, re
from annotation.models import SecondStageWorkPool, FirstStageWorkPool

# 根据找到的修正信息进行HTML渲染
dic_error_indexs = {
    1: '名词',
    2: '动词',
    3: '形容词',
    4: '数量',
    5: '细化',
}
def _tohtml(old_word, new_word, error_kind):    
    if error_kind == '名词':
        tohtml = '<span style="background-color:HotPink; margin: 0px 1px;" title=名词：' + old_word + '>' + new_word + '</span>';
    elif error_kind == '动词':
        tohtml = '<span style="background-color:Tomato; margin: 0px 1px;" title=动词：' + old_word + '>' + new_word + '</span>';
    elif error_kind == '形容词':
        tohtml = '<span style="background-color:DeepSkyBlue; margin: 0px 1px;" title=形容词：' + old_word + '>' + new_word + '</span>';
    elif error_kind == '数量':
        tohtml = '<span style="background-color:PaleGreen; margin: 0px 1px;" title=数量：' + old_word + '>' + new_word + '</span>';
    elif error_kind == '细化':
        tohtml = '<span style="background-color:MediumOrchid; margin: 0px 1px;" title=细化：' + old_word + '>' + new_word + '</span>';

    return tohtml

# 将看图片标注的中文转换为HTML代码
def html_zh(zh, fix_infos):
    old_words = [i.word_before_change for i in fix_infos]
    new_words = [i.word_after_change for i in fix_infos]
    error_kinds = [dic_error_indexs[i.which_classification] for i in fix_infos]
    new_words_pos = [(i.word_after_change_start_pos, i.word_after_change_end_pos) for i in fix_infos]

    # 为被修正的部分
    word_list = []
    pre_i = 0
    for i, j in new_words_pos: 
        word_list.append(zh[pre_i:i])
        pre_i = j
    word_list.append(zh[pre_i:])
    
    # 生成HTML中文
    index = 0
    new_zh = word_list[index]
    for i, j, k in zip(old_words, new_words, error_kinds):
        tohtml = _tohtml(i, j, k)
        index += 1
        new_zh = new_zh + tohtml + word_list[index]

    return new_zh

# 解析看图片标注的中文HTML代码
def parse(zh):
    '''
        return: old_words：修正之前单词的列表
                old_words_pos：修正之前单词在旧中文中的位置，元素是元组，表示开始和结束位置（左闭右开区间）
                new_words：修正之后单词的列表
                new_words_pos：修正之后单词在新中文中的位置，元素是元组，表示开始和结束位置（左闭右开区间）
                type_list：修正类型列表
                zh：修正之后的中文
    '''
    if '<span' not in zh:
        # 无修正直接返回即可
        return None, None, None, None, None, zh

    tmp1 = [i.end() for i in re.finditer('title="', zh)]
    tmp2 = [i.start() for i in re.finditer('">', zh)]
    assert len(tmp1) == len(tmp2)

    old_words, type_list = [], []
    for i,j in zip(tmp1, tmp2):
        t = zh[i:j].split('：')
        assert len(t) == 2
        type_list.append(t[0])
        old_words.append(t[-1])

    tmp1 = [i.end() for i in re.finditer('">', zh)]
    tmp2 = [i.start() for i in re.finditer('</span>', zh)]
    assert len(tmp1) == len(tmp2)

    new_words = []
    for i,j in zip(tmp1, tmp2):
        new_words.append(zh[i:j])

    x = re.split(r'<span.*?</span>', zh)
    assert len(old_words) == len(new_words) == len(type_list) == len(x)-1
    
    old_words_pos = []
    # 计算修正前单词在旧中文中的位置
    index = 0
    t = len(x[index])
    for i in old_words:
        l = len(i)
        old_words_pos.append((t, t+l))
        index += 1
        t += l + len(x[index])
        
    new_words_pos = []
    # 计算修正后单词在新中文中的位置
    index = 0
    t = len(x[index])
    for i in new_words:
        l = len(i)
        new_words_pos.append((t, t+l))
        index += 1
        t += l + len(x[index])
    
    assert len(old_words) == len(old_words_pos) == len(new_words_pos)

    # 得到修正之后的中文
    for i in new_words:
        zh = re.sub(r'<span(.*?)</span>', i, zh, 1)

    return old_words, old_words_pos, new_words, new_words_pos, type_list, zh

# 将图片名字转换为url路径
def image_url(image_name):
    path_list = ['img', 'coco']
    path_list.extend(image_name.split('_'))
    return os.path.join(*path_list)

# 得到用户的不看图片标注任务总量
def get_total_amount_without_image(user_obj):
    return len(FirstStageWorkPool.objects.filter(user_obj=user_obj).all())

# 得到用户的看图片标注任务总量
def get_total_amount_with_image(user_obj):
    return len(SecondStageWorkPool.objects.filter(user_obj=user_obj).all())

# 得到用户第二阶段任务的第一个未完成任务的索引
def get_first_isnot_finished_index(user_obj):
    t = SecondStageWorkPool.objects.filter(user_obj=user_obj).all()
    for index, i in enumerate(t):
        if i.is_finished == False:
            return index + 1

    return get_total_amount_with_image(user_obj) + 1

# 得到用户第二阶段未完成任务的总数
def get_isnot_finished_amout(user_obj):
    num = 0
    t = SecondStageWorkPool.objects.filter(user_obj=user_obj).all()
    for i in t:
        if i.is_finished == False:
            num += 1

    return num