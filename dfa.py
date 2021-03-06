import copy
import enum
from pkg_resources import register_namespace_handler
from pypinyin import lazy_pinyin
from pypinyin.core import pinyin
from hanzi_chaizi import HanziChaizi as hc
def other_char_cn(char):
    if(ord(char) >= 32 and ord(char) <= 126):
        if(char>='0'and char<='9'):
            return False
        if(char>='A' and char<='Z'):
            return False
        if(char>='a' and char<='z'):
            return False
        return True
    else:
        return False
def other_char_en(char):
    if(ord(char) >= 32 and ord(char) <= 126):
        if(char>='A' and char<='Z'):
            return False
        if(char>='a' and char<='z'):
            return False
        return True
    else:
        return False
def is_alpha(char):
    if(char>='A' and char<='Z'):
        return True
    elif(char>='a' and char<='z'):
        return True
    else:
        return False
def check_pinyin(char,pinyin):
    if(lazy_pinyin(char)[0] == pinyin):
        return True
    else:
        return False
def check_match(char,ch,state):
    if(len(ch)!=1):
        return 0
    #英文匹配
    if(char==ch and is_alpha(char)):
        return 1
    #中文匹配
    elif(char==ch):
        return 2
    #谐音匹配
    elif(ord(char)>127 and ord(ch)>127 and check_pinyin(char,state[ch]["pinyin"])):
        return 3
    #首字母匹配
    elif(is_alpha(char) and ord(ch)>127 and state[ch]["pinyin"][0]==char):
        return 4
    #偏旁匹配
    elif(ord(char)>127 and ord(ch)>127 and state[ch]["chaizi"][0]==char):
        return 5
    else:
        return 0
class DFA:

    def __init__(self, keyword_list: list):
        self.state_event_dict = self._generate_state_event_dict(keyword_list)

    def match(self, content: str):
        match_list = []
        temp_match_list = []
        state_list = []
        #查找一行中的每个字
        for char_pos, char in enumerate(content):
            #找到第一个字
            for idx,ch in enumerate(self.state_event_dict):
                if(len(ch)!=1):continue
                if(check_match(char,ch,self.state_event_dict)):
                    state_list.append(self.state_event_dict)
                    temp_match_list.append({
                        "match":"",
                        "keyword":"",
                        "cur_pinyin":"",
                        "cur_chaizi":"",
                        "finish":0,
                        "other":0
                    })
            #更新状态
            #倒序遍历，以防删除元素后发生错误
            for index in range(len(state_list)-1,-1,-1):
                state=state_list[index]
                for idx,ch in enumerate(state):
                    if(len(ch)!=1):continue
                    #英文匹配
                    if(check_match(char,ch,state)==1):
                        state_list[index] = state[char]
                        temp_match_list[index]["match"] += char
                        temp_match_list[index]["keyword"] += char
                        temp_match_list[index]["finish"] = 1
                        #找到完整关键词
                        if state[char]["is_end"]:
                            match_list.append(copy.deepcopy(temp_match_list[index]))
                    elif(check_match(char,ch,state)==2):
                        if(temp_match_list[index]["finish"]==1):
                            state_list[index] = state[char]
                            temp_match_list[index]["match"] += char
                            temp_match_list[index]["keyword"] += char
                            temp_match_list[index]["finish"] = 1
                            #找到完整关键词
                            if state[char]["is_end"]:
                                match_list.append(copy.deepcopy(temp_match_list[index]))
                    elif(check_match(char,ch,state)==3):
                        if(temp_match_list[index]["finish"]==1):
                            state_list[index] = state[ch]
                            temp_match_list[index]["match"] += char
                            temp_match_list[index]["keyword"] += ch
                            temp_match_list[index]["finish"] = 1
                            if state[char]["is_end"]:
                                match_list.append(copy.deepcopy(temp_match_list[index]))
                    elif(check_match(char,ch,state)==4):
                        #finish表示拼音拼到一半或偏旁匹配到一半，不进入语句
                        if(temp_match_list[index]["finish"]==1):
                            state_list[index] = state[ch]
                            temp_match_list[index]["match"] += char
                            temp_match_list[index]["keyword"] += ch
                            temp_match_list[index]["finish"] = 1
                            temp_match_list[index]["cur_pinyin"] = char
                            if state[char]["is_end"]:
                                match_list.append(copy.deepcopy(temp_match_list[index]))
                    elif(check_match(char,ch,state)==5):
                        if(temp_match_list[index]["finish"]==1):
                            state_list[index] = state[ch]
                            temp_match_list[index]["match"] += char
                            temp_match_list[index]["keyword"] += ch
                            temp_match_list[index]["finish"] = 0
                            temp_match_list[index]["cur_chaizi"] = char
                            if state[char]["is_end"]:
                                match_list.append(copy.deepcopy(temp_match_list[index]))
                    #拼音非首字母
                    elif(is_alpha(char) and ord(ch)>127):
                        #拼音结尾
                        if(temp_match_list[index]["cur_pinyin"]+char==state[ch]["pinyin"]):
                            temp_match_list[index]["cur_pinyin"]+=char
                            temp_match_list[index]["finish"]=1
                            temp_match_list[index]["match"]+=char
                        #中间的拼音
                        elif(temp_match_list[index]["cur_pinyin"]+char in state[ch]["pinyin"]):
                            temp_match_list[index]["cur_pinyin"]+=char
                            temp_match_list[index]["finish"]=0
                            temp_match_list[index]["match"]+=char
                    #偏旁后的字根
                    elif(ord(char)>127 and ord(ch)>127 and 
                    temp_match_list[index]["cur_chaizi"]+char==state[ch]["chaizi"]):
                        temp_match_list[index]["cur_chaizi"]+=char
                        temp_match_list[index]["finish"]=1
                        temp_match_list[index]["match"]+=char
                    #英文遇到其他字符
                    elif(temp_match_list[index]["other"]<20 and 
                    is_alpha(ch) and other_char_en(char)):
                        temp_match_list[index]["other"] += 1
                        temp_match_list[index]["match"] += char
                    #中文其他字符
                    elif(temp_match_list[index]["other"]<20 and 
                    ord(ch)>127 and other_char_cn(char)):
                        temp_match_list[index]["other"] += 1
                        temp_match_list[index]["match"] += char
                    #重新检测敏感词
                    else:
                        if(idx==len(state)-1):
                            state_list.pop(index)
                            temp_match_list.pop(index)
                        #没有状态了
                        if(len(state_list)<1):
                            break

        return match_list

    @staticmethod
    def _generate_state_event_dict(keyword_list: list) -> dict:
        state_event_dict = {}

        for keyword in keyword_list:
            current_dict = state_event_dict
            length = len(keyword)

            for index, char in enumerate(keyword):
                #if(is_alpha(char)):
                #    char=char.lower()
                if char not in current_dict:
                    next_dict = {"is_end": False,"pinyin":"","chaizi":""}
                    current_dict[char] = next_dict
                    current_dict = next_dict
                    #char是中文
                    if(ord(char)>127):
                        current_dict['pinyin']=lazy_pinyin(char)[0]
                        if(len(hc().query(char))):
                            current_dict['chaizi']=hc().query(char)[0]+hc().query(char)[1]

                else:
                    next_dict = current_dict[char]
                    current_dict = next_dict

                if index == length - 1:
                    current_dict["is_end"] = True

        return state_event_dict


if __name__ == "__main__":
    dfa = DFA(["fuck","fqwe"])
    #print(dfa.state_event_dict)
    print(dfa.match("fuck"))
#fu__&^&%&^ckansfawe


    '''         if(char in state):
                    state_list[index] = state[char]
                    temp_match_list[index]["match"] += char
                    temp_match_list[index]["keyword"] += char
                    #找到完整关键词
                    if state[char]["is_end"]:
                        match_list.append(copy.deepcopy(temp_match_list[index]))
                #遇到其他字符
                elif(temp_match_list[index]["other"]<20 and other_char_en(char)):
                    temp_match_list[index]["other"] += 1
                    temp_match_list[index]["match"] += char
                #重新检测敏感词
                else:
                    state_list.pop(index)
                    temp_match_list.pop(index)
                    '''