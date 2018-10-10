from aip import AipSpeech
from commonlib import *
import json



if __name__=='__main__':

    #检查是否能获得运行权限锁,保证只有一个实例在运行
    lockfile = __file__ + ".lock"
    if not try_lock(lockfile):
        print("get lock fail, so exit ...")
        sys.exit(0)
        
    print("get lock succ, so continue ...")
    
    init_aip()
    init_db()

    result = get_result("select title, cid, data from content_info where state = 1 and (voice_state is null or voice_state = 0) order by create_time desc limit 5")
    
    for content in result:
        title = content[0]
        cid = content[1]
        data = get_text_from_html(content[2])

        sentences = get_sentence(data)
        #print(sentences)

        content_info = {}
        content_info["data"] = sentences
        
        sdata = json.dumps(content_info, ensure_ascii=False) 
        #print(sdata) 

        #首先保证有目录
        path = "./data/" + cid + "/"
        if not os.path.exists(path):
            os.mkdir(path)

        #添加title的朗读
        succ = get_tts(title, path + "0.mp3")
        if not succ:
            #转换出错了
            print("get title tts error! data:", title, " cid:", cid)
            continue

        #逐行转换
        index = 1
        for s in sentences: 
            filename = "%s%d.mp3" % (path, index) 
            print("Handle ", filename)
            succ = get_tts(s, filename)
            if not succ:
                print("get tts error! data:", s, " cid:", cid)
                break
            index = index + 1

        #发生错误，则直接跳过
        if not succ: 
            continue
    
        #回写状态和数据
        sql = "update content_info set sdata='%s', voice_state=1 where cid='%s'" % (escape_str(sdata), cid)
        get_result(sql)



