import tkinter,os
import IniCompare

signalInivalue= {}
messID        = []
rollMax       = 0
def windowForChoose(messID,signalInivalue,msg_queue):
    checkButtonVar = {}
    varForCheck    = tkinter.IntVar()
    sonWin         = tkinter.Toplevel()
    sonWin.config(width=200)
    Label_Remind   = tkinter.Label(sonWin, text='          勾选需要生成代码的对象            ')
    Label_Remind.pack()

    for i in messID:
        checkButtonVar[i]=tkinter.IntVar()
        checkButton1 = tkinter.Checkbutton(sonWin,text=i,variable=checkButtonVar[i],onvalue=1,offvalue=0)
        checkButton1.pack()
    buttonForConfirm = tkinter.Button(sonWin, text='确认并生成代码', bg='#DCDCDC',
                                      command=lambda :[sonWin.destroy(),
                                                       codeGenerate(signalInivalue, checkButtonVar, msg_queue)])
    buttonForConfirm.pack()
    msg_queue.put("20%. dbc 所需数据及格式 读取完毕...")

def codeGenerate(signalInivalue,checkButtonVar,msg_queue):
    # 先把选中的signal 清理一遍，保留打勾的sig,暂时删除checksum 减少遍历时间
    numOfRollSig = 0;
    for value in list(signalInivalue.keys()):
        if checkButtonVar[ hex(eval(value)) ].get() == 0:               #丢弃未打勾的
            del signalInivalue[value]
    for value in list(signalInivalue.keys()):                           # 该版本不支持checksum 的校验。故丢弃,后续补充
        for value_del in list(signalInivalue[value].keys()):
            if 'ROLL'     in value_del.upper():                         #选中的报文中包含ROLL的总数量
                numOfRollSig += 1
            if 'CHECKSUM' in value_del.upper():
                del  signalInivalue[value][value_del]
    msg_queue.put('40% 勾选的message 内容筛选OK...')
    #读第一个messID
    thisID   = list(signalInivalue.keys())[0]
    firstID  = thisID

    #写入头部代码
    target_txt       = open('targetCpal.txt','a')
    target_txt.write('includes{'
                     '\n//脚本中rollingCount 最大值取第一个roll的最大值，请视情况修改'
                     '\n}\n\n')
    target_txt.write('variables'
                     '\n{{\n'
                     '  int CurRollCount[{}] = {{ {} }};\n'
                     '  int HisRollCount[{}] = {{ {} }};\n'
                     '  int rollMax          =  {} ;\n'
                     '}}\n\n'.format(numOfRollSig, ('0,'*numOfRollSig).strip(','),
                                     numOfRollSig, ('0,'*numOfRollSig).strip(','),rollMax))
    numOfRollSig     = 0; numOfRollSta =0
    #读取每个信号携带的mess ID,ini并写出对比代码
    for value in signalInivalue:
        str_writeForCurR = ''
        str_writeForHisR = ''
        target_txt.write(     '\non message {} {{\n'.format(value))
        for value_sig in signalInivalue[value]:
            if 'ROLL' not in value_sig.upper():
                target_txt.write(
                              '\n  if (this.{} != {})'
                              '\n    {{'
                              '\n    write("%d initial error,but {} in dbc",this.{});'
                              '\n    }}\n'
                                 .format(value_sig, signalInivalue[value][value_sig],
                                         signalInivalue[value][value_sig], value_sig))

            elif  'ROLL' in value_sig.upper():
                numOfRollSig += 1
                str_writeForCurR = str_writeForCurR + '  CurRollCount[{}] = this.{};\n'\
                             .format(numOfRollSig - 1, value_sig)
                str_writeForHisR = str_writeForHisR + '  HisRollCount[{}] = CurRollCount[{}];\n'\
                             .format(numOfRollSig - 1, numOfRollSig - 1)

        #写出roll的判断代码再结束这条mess
        numOfRollEnd = numOfRollSig
        target_txt.write('\n' + str_writeForCurR + '\n')
        target_txt.write(     '\n  for (i={};i<={};i++){{'
                              '\n      if ((CurRollCount[i])-HisRollCount[i]==1 || (CurRollCount[i])-HisRollCount[i]==-rollMax)' #考虑加入最大值判断
                              '\n          {{ }}'
                              '\n      else{{'
                              '\n          write("Roll error,ID:{},time:%f", timeNow()/100000.0);'
                              '\n          }}'
                              '\n      }}\n'
                     .format(numOfRollSta,numOfRollEnd-1,value))
        target_txt.write('\n' + str_writeForHisR + '\n')
        numOfRollSta = numOfRollSig
        target_txt.write('}\n')
    msg_queue.put('80% 代码生成结束...')
    target_txt.close()
    msg_queue.put('100% 文档关闭,targetCpal.txt 生成在本地目录')

def iniCompare(dbc_path,msg_queue):
    global rollMax
    if dbc_path=='nofile':
        msg_queue.put('Error: no file chosed')
        return
    msg_queue.put('生成的脚本默认替换当前目录下同名文件')
    #读取数据并以合适的格式给出
    source_dbc = open(dbc_path,'r',encoding='ANSI')
    dbc_lines = source_dbc.readlines()
    messID=[]
    flag_findMaxRoll = 0

    for i_line in dbc_lines:

        if i_line.split(' ')[0] == 'BO_':
            thisMessageID = hex(eval(i_line.split(' ')[1]))
            messID.append(thisMessageID)
            signalInivalue[thisMessageID]  = {}

        if i_line.strip(' ').split(' ')[0] == 'SG_':
            signalInivalue[thisMessageID][i_line.strip(' ').split(' ')[1]] = 0                                           # {messageID:{sig:ini_1;sig2:ini_2}}
            if flag_findMaxRoll == 1:
                continue
            if 'ROLL' in i_line.strip(' ').split(' ')[1].upper():
                rollMax= i_line.strip(' ').split(' ')[5].strip('[]').split('|')[1]                                          #当前默认所有的rollcounter一致
                flag_findMaxRoll =1
        if i_line.split(' ')[0] == 'BA_' and i_line.count('GenSigStartValue')>0:
            signalInivalue[hex(eval(i_line.split(' ')[3]))] [i_line.split(' ')[4]] =  i_line.split(' ')[5].strip(';\n')
        #记录每个信号的checksum
        #if i_line.split(' ')[0] == 'CM_' and i_line.split(' ')[1] == 'SG_':

    source_dbc.close()
    messID.sort()
    windowForChoose(messID, signalInivalue, msg_queue)


