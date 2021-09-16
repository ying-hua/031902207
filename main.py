import dfa
import sys
#python main.py D:\MyProgramPy\twords.txt D:\MyProgramPy\torg.txt D:\MyProgramPy\tans.txt
if __name__ == "__main__":
    if(len(sys.argv)!=4):
        print("参数个数错误")
        exit(0)
    words_f=open(sys.argv[1],'r',encoding='utf-8')
    words=words_f.readlines()
    for idx,content in enumerate(words):
        words[idx]=content.strip('\n')
    word_map={}
    temp_words=[]
    #将关键词的英文处理成小写，再和原词映射
    for word in words:
        low_word=word.lower()
        temp_words.append(low_word)
        word_map[low_word]=word
    words_f.close()
    words_match=dfa.DFA(temp_words)
    org_f=open(sys.argv[2],'r',encoding='utf-8')
    orgs=org_f.readlines()
    org_f.close()
    ans_list=[]
    total=0
    for idx,line in enumerate(orgs):
        ans_list.append(words_match.match(line))
        total+=len(ans_list[idx])
        if(idx==246):
            print(line)
    ans_f=open(sys.argv[3],'w')
    ans_f.write("Total: "+str(total)+'\n')
    #print(word_map)
    for idx,line in enumerate(ans_list):
        for word in line:
            ans_f.write("Line"+str(idx+1)+": <"+word_map[word["keyword"]]+"> "+word["match"]+'\n')
    ans_f.close()
    #python main.py D:\MyProgramPy\twords.txt D:\MyProgramPy\torg.txt D:\MyProgramPy\tans.txt