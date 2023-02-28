import tkinter
import IniCompare
import xlrd
import xlwt
import queue
import os

#后面版本代码可以复用了，但不想改了，太麻烦了


def ExcelToDbc(msg_queue,CANFD_flag,mtx_pathT):
    #这个CANflag指示了excel将转换的格式为FD
    prgprc = '初始化...\nproduct at 2022-10-19  x\n'
    msg_queue.put(prgprc)

    '''该函数生成dbc要求格式的BA_属性 list 转 str'''
    def list_to_str(messType, valueList):
        str_return = ''
        if messType == 'INT':
            for i in valueList:
                str_return = str_return + str(i) + ' '
            str_return = str_return.strip(' ') + ';'
            return str_return
        if messType == 'ENUM':
            for i in valueList:
                str_return = str_return + '"{}"'.format(i) + ','
            str_return = str_return.strip(',') + ';'
            return str_return
        if messType == 'STRING':
            for i in valueList:
                str_return = str_return + '"{}"'.format(i) + ','
            str_return = str_return.strip(',') + ';'
            return str_return
        else:
            for i in valueList:
                str_return = str_return + '"{}"'.format(i) + ','
            str_return = str_return.strip(',') + ';'
            return str_return

    #对 name 格式进行检查
    def Warning_Check(li):
        for item in li:
            if item=='':
                msg_queue.put('!!!warning 将未填入的空自动填入‘/’,请自行确认')
            if item.strip(' ').count(' ') > 0 or(item.count('-')>0)\
                    or (item.count('.')>0):
                prgprc = '!!!warning {}存在空格或不规范,请自行确认'.format(item)
                msg_queue.put(prgprc)

    #对读取到的value table 进行转化为连续table
    def Change_valueTable(valueList):
        value_return = ''
        valueList = valueList.replace('~', '-').strip('\n').split('\n')
        for i in valueList:
            if i == '':
                continue
            i = i.replace('：', ':').split(':')
            if i[0].count('-') > 0:
                j = i[0].split('-')
                if eval(j[1])-eval(j[0])>20:
                    msg_queue.put('!!!warning   超长(>20)value已删除，请自行确认{}\n'.format(i))
                    continue
                k = ''
                for str1 in range(eval(j[0]), eval(j[1]) + 1):
                    value_return = value_return + '{} "{}" '.format(str1, i[1])
            else:
                value_return = value_return + '{} "{}" '.format(eval(i[0]), i[1])

        return value_return

    #byte order 仅能通过Mo inter 字符判断
    transmitter_col = 1
    receiver_col    = 2
    signalName_col  = 3
    description_col = 4
    messageName_col = 5
    messageID_col   = 6
    messageType_col = 7
    period_col      = 8
    messageDlc_col  = 9
    Msb_col =        10
    Lsb_col =        11
    signalSize_col = 12
    byteOrder_col =  13
    dataType_col =   14
    signalDefIniValue_col = 15
    factor_col =     17
    offset_col =     18
    minValue_col =   19
    maxValue_col =   20
    unit_col =       21
    coding_col =     22

    '''新建一个dbc文件'''
    dbc_write = open('target.dbc', 'a')
    dbc_write.close()
    os.remove('target.dbc')
    dbc_write = open('target.dbc', 'a', encoding='ansi')

    '''打开源excel文件，预操作'''
    excel_read = xlrd.open_workbook(mtx_pathT, 'r', encoding_override='utf-8')
    sheet_read = excel_read.sheet_by_index(3)
    rowsNum    = sheet_read.nrows
    prgprc     = "读取模板结束\n"
    msg_queue.put(prgprc)

    '''预处理transmitter'''
    transmitter_value = sheet_read.col_values(transmitter_col)
    Warning_Check(transmitter_value)
    for i in range(1, len(transmitter_value)):
        if transmitter_value[i] == '':
            transmitter_value[i] = '/'
            continue
        if transmitter_value[i] == '/':
            continue
        else:
            transmitter_value[i] = transmitter_value[i] \
                .replace(' ', '').strip(',').replace('/', ',').replace('-', '_')
    '''预处理receiver'''
    receiver_value = sheet_read.col_values(receiver_col)
    Warning_Check(receiver_value)
    for i in range(1, len(receiver_value)):
        if receiver_value[i] == '':
            receiver_value[i] = '/'
            continue
        if receiver_value[i] == '/':
            continue
        else:
            receiver_value[i] = receiver_value[i]. \
                replace(' ', '').strip(',').replace('/', ',').replace('-', '_')

    '''预处理signal_name'''
    signalName_value = sheet_read.col_values(signalName_col)
    Warning_Check(signalName_value)
    for i in range(1, len(signalName_value)):
        signalName_value[i] = signalName_value[i]. \
            replace(' ', '').replace('-', '_')

    '''预处理description'''
    description_value = sheet_read.col_values(description_col)

    '''预处理Message_ID'''
    messageID_value = sheet_read.col_values(messageID_col)
    for i in range(1, len(messageID_value)):

        messageID_value[i] = messageID_value[i]. \
            replace('E', 'e').replace('x', 'X').replace(' ', '')
    '''预处理Msb和Lsb'''
    Msb_value = sheet_read.col_values(Msb_col)
    Lsb_value = sheet_read.col_values(Lsb_col)
    for i_value in range(1,len(Msb_value)):
        if Msb_value[i_value] == '/':
            Msb_value[i_value]=0
    for i_value in range(1,len(Lsb_value)):
        if Lsb_value[i_value] == '/':
            Lsb_value[i_value]=0

    '''预处理factor'''
    factor_value = sheet_read.col_values(factor_col)
    for i in range(1, len(factor_value)):
        if type(factor_value) == 'str':
            if factor_value[i].replace(' ', '') == '/':
                factor_value = 0
            else:
                factor_value[i] = factor_value[i].replace(' ', '')
        else:
            factor_value[i]=str(factor_value[i])
    '''预处理Offset'''
    offset_value = sheet_read.col_values(offset_col)
    for i in range(1, len(offset_value)):
        if type(offset_value) == 'str':
            if offset_value[i].replace(' ', '') == '/':
                offset_value = 0
            else:
                offset_value[i] = offset_value[i].replace(' ', '')
        else:
            offset_value[i]=str(offset_value[i])
    '''预处理max min 物理值'''
    minValue_value = sheet_read.col_values(minValue_col)
    maxValue_value = sheet_read.col_values(maxValue_col)
    for i in range(1, len(minValue_value)):
        if minValue_value[i] == '/':
            minValue_value[i] = 0
            continue
        if type(minValue_value[i]) == str:
            minValue_value[i] = eval(minValue_value[i].replace(' ', ''))
    for i in range(1, len(maxValue_value)):
        if maxValue_value[i] == '/':
            maxValue_value[i] = 0
            continue
        if type(maxValue_value[i]) == str:
            maxValue_value[i] = eval(maxValue_value[i].replace(' ', ''))
    '''预处理Inidefvalue'''
    signalDefIniValue_value = sheet_read.col_values(signalDefIniValue_col)
    for i in range(1,len(signalDefIniValue_value)):
        signalDefIniValue_value[i]=str(signalDefIniValue_value[i]).replace(' ','')
        if signalDefIniValue_value[i]=='/':
            signalDefIniValue_value[i]=0
            continue
        if signalDefIniValue_value[i].count('x')>0 or signalDefIniValue_value[i].count('X')>0:
            signalDefIniValue_value[i]=eval(signalDefIniValue_value[i])
            continue
        else:
            signalDefIniValue_value[i] = str(signalDefIniValue_value[i])
            signalDefIniValue_value[i] = \
                (eval(signalDefIniValue_value[i]) - eval(offset_value[i])) / eval(factor_value[i])

    '''预处理coding/暂不额外处理'''
    value_value = sheet_read.col_values(coding_col)


    '''预设置通用属性'''
    sheet_Gen_read = excel_read.sheet_by_index(1)
    if CANFD_flag==0:
        Gen_rownum=[1,10]
    if CANFD_flag==1:
        Gen_rownum=[13,32]
    Gen_colnum = sheet_Gen_read.ncols
    BA_list = {}
    for i in range(Gen_rownum[0], Gen_rownum[1]+1):
        BA_valueList = []
        BA_type      = sheet_Gen_read.cell_value(i, 1)
        BA_name      = sheet_Gen_read.cell_value(i, 2)
        BA_valueType = sheet_Gen_read.cell_value(i, 3)
        for j in range(4, Gen_colnum):
            if sheet_Gen_read.cell_value(i,j) =='':
                BA_list[BA_name] = [BA_type, BA_valueType, BA_valueList]
                continue
            if sheet_Gen_read.cell_value(i, j) != '':
                if BA_valueType == 'INT':
                    BA_valueList.append(int(sheet_Gen_read.cell_value(i, j)))
                else:
                    BA_valueList.append(sheet_Gen_read.cell_value(i, j))
            BA_list[BA_name] = [BA_type, BA_valueType, BA_valueList]



    '''读取并写入总括内容'''
    dbc_write.write('VERSION ""\n\n\n')
    dbc_write.write('NS_ :\n')
    dbc_write.write('   NS_DESC_\n        CM_\n              BA_DEF_\n       BA_\n           VAL_\n         CAT_DEF_\n'     
                    '   CAT_\n            FILTER\n           BA_DEF_DEF_\n   EV_DATA_\n      ENVVAR_DATA_\n SGTYPE_\n'      
                    '   SGTYPE_VAL_\n     BA_DEF_SGTYPE_\n   BA_SGTYPE_\n    SIG_TYPE_REF_\n VAL_TABLE_\n   SIG_GROUP_\n' 
                    '   SIG_VALTYPE_\n    SIGTYPE_VALTYPE_\n BO_TX_BU_\n     BA_DEF_REL_\n   BA_REL_\n'
                    '   BA_DEF_DEF_REL_\n BU_SG_REL_\n       BU_EV_REL_\n    BU_BO_REL_\n    SG_MUL_VAL_\n\n')

    '''读取并写入BS_比特率'''
    dbc_write.write('BS_:\n\n')

    '''读取并写入BU_网络节点'''
    dbc_write.write('BU_:')
    BU_nodes = []
    BAforBO_ = {}
    valuetable = []
    for i in range(1, rowsNum):
        BAforBO_[messageID_value[i]] = \
            [sheet_read.cell_value(i, messageType_col), sheet_read.cell_value(i, period_col)]
        valuetable.append([messageID_value[i],
                           signalName_value[i], sheet_read.cell_value(i, coding_col)])
    for i in range(1, len(transmitter_value)):
        if transmitter_value[i].count(',') > 0:
            for j in transmitter_value[i].split(','):
                BU_nodes.append(j)
        else:
            BU_nodes.append(transmitter_value[i])
    for i in range(1, len(receiver_value)):
        if receiver_value[i].count(',') > 0:
            for j in receiver_value[i].split(','):
                BU_nodes.append(j)
        else:
            BU_nodes.append(receiver_value[i])
    BU_nodes = list(set(BU_nodes))
    if '/' in BU_nodes:
        BU_nodes.remove('/')
    for i in BU_nodes:
        dbc_write.write(i + ' ')
    dbc_write.write('\n\n')
    prgprc = '1/5 写入BU结束\n'
    msg_queue.put(prgprc)

    '''读取并写入BO_消息报文'''
    bo_tx_bu = []
    BAforSG_ = {}
    BAforSG_signalList = []
    '''---试写第一行,保存个别属性特征后期使用'''
    messID_current=messageID_value[1]
    dbc_write.write('BO_ {} {}: {} {}\n'
                    .format(eval(messID_current),
                    sheet_read.cell_value(1, messageName_col),
                    int(sheet_read.cell_value(1, messageDlc_col)),
                    [transmitter_value[1].split(',')[0],'Vector__XXX'][transmitter_value[1]=='/']
                    ))
    if transmitter_value[1].count(',') > 0:
        bo_tx_bu.append([eval(messageID_value[1]),transmitter_value[1]])

    '''---开始遍历写入'''
    for i in range(1, rowsNum):
        messID_thiscol=messageID_value[i]
        if messID_current == messID_thiscol:
            dbc_write.write(' SG_ {} : {}|{}@{}{} ({},{}) [{}|{}] "{}" {}\n'.format(
                signalName_value[i],
                [int(Msb_value[i]), int(Lsb_value[i])]
                [len(sheet_read.cell_value(i, byteOrder_col)) < 6],
                int(sheet_read.cell_value(i, signalSize_col)),
                ['1', '0'][len(sheet_read.cell_value(i, byteOrder_col)) > 6],
                ['-', '+'][len(sheet_read.cell_value(i, dataType_col)) == 8],
                factor_value[i], offset_value[i], minValue_value[i], maxValue_value[i],
                ['', sheet_read.cell_value(i, unit_col)][sheet_read.cell_value(i, unit_col) != '/'],
                ['Vector__XXX', receiver_value[i]][receiver_value[i] != '/']
            ))
            BAforSG_signalList. \
                append([signalName_value[i], signalDefIniValue_value[i]])
            BAforSG_[messID_current] = BAforSG_signalList
        else:
            messID_current = messID_thiscol
            BAforSG_signalList = []
            dbc_write.write('BO_ {} {}: {} {}\n'.format(
                eval(messID_thiscol),
                sheet_read.cell_value(i, messageName_col),
                int(sheet_read.cell_value(i, messageDlc_col)),
                [transmitter_value[1].split(',')[0],'Vector__XXX'][transmitter_value[1]=='/']
            ))
            if transmitter_value[i].count(',') > 0:
                bo_tx_bu.append([eval(messID_thiscol), transmitter_value[i]])

            dbc_write.write(' SG_ {} : {}|{}@{}{} ({},{}) [{}|{}] "{}" {}\n'.format(
                signalName_value[i],
                [int(Msb_value[i]), int(Lsb_value[i])]
                [len(sheet_read.cell_value(i, byteOrder_col)) < 6],
                int(sheet_read.cell_value(i, signalSize_col)),
                ['1', '0'][len(sheet_read.cell_value(i, byteOrder_col)) > 6],
                ['-', '+'][len(sheet_read.cell_value(i, dataType_col)) == 8],
                factor_value[i], offset_value[i], minValue_value[i], maxValue_value[i],
                ['', sheet_read.cell_value(i, unit_col)][sheet_read.cell_value(i, unit_col) != '/'],
                ['Vector__XXX', receiver_value[i]][receiver_value[i] != '/']
            ))
            BAforSG_signalList. \
                append([signalName_value[i], signalDefIniValue_value[i]])
            BAforSG_[messID_current] = BAforSG_signalList
    prgprc = '2/5 写入BO_结束\n'
    msg_queue.put(prgprc)

    '''判断并写入BO_TX_BU_ : '''
    dbc_write.write('\n')
    if len(bo_tx_bu) > 0:
        for i in range(0, len(bo_tx_bu)):
            dbc_write.write('BO_TX_BU_ {} : {};\n'.format(bo_tx_bu[i][0], bo_tx_bu[i][1]))
    else:
        dbc_write.write('\n')
    prgprc = '3/5 写入BO_TX_BU_ 结束\n'
    msg_queue.put(prgprc)

    '''读取并写入CM_ SG_ '''
    msg_queue.put('默认写入description')
    for i in range(1,len(description_value)):
        dbc_write.write('CM_ SG_ {} {} "{}";\n'.
                        format(eval(messageID_value[i]),signalName_value[i],description_value[i]))

    '''写入BA_属性'''
    for i in BA_list:
        if BA_list[i][0]=='NA':
            dbc_write.write('BA_DEF_ "{}" {};\n'.format(i, BA_list[i][1]))
        else:
            dbc_write.write('BA_DEF_ {} "{}" {} {}\n'.format(
                BA_list[i][0], i, BA_list[i][1], list_to_str(BA_list[i][1], BA_list[i][2])))
    for i in BA_list:
        if BA_list[i][0] == 'NA':
            dbc_write.write('BA_DEF_DEF_ "{}" "";\n'.format(i))
            continue
        if BA_list[i][2]==[]:
            dbc_write.write('BA_DEF_DEF_ "{}" "";\n'.format(i))
            continue
        if BA_list[i][1] == 'INT':
            dbc_write.write('BA_DEF_DEF_ "{}" {};\n'.format(i, BA_list[i][2][0]))
        else:
            dbc_write.write('BA_DEF_DEF_ "{}" "{}";\n'.format(i, BA_list[i][2][0]))
    prgprc = '4/5 写入BA_属性结束\n'
    msg_queue.put(prgprc)


    '''读取并写入BA＿赋值信息:默认值情况下不写入，有值发生更改，则分别输出'''
    for i in BAforBO_:
        if BAforBO_[i][0] == 'E':
            dbc_write.write('BA_ "GenMsgSendType" BO_ {} {};\n'.format(eval(i), 1))
        if BAforBO_[i][0] == 'P' and BAforBO_[i][1] != 0:
            dbc_write.write('BA_ "GenMsgSendType" BO_ {} {};\n'.format(eval(i), 0))
            dbc_write.write('BA_ "GenMsgCycleTime" BO_ {} {};\n'.format(eval(i), BAforBO_[i][1]))
        if CANFD_flag==1:
            dbc_write.write('BA_ "VFrameFormat" BO_ {} {};\n'.format(eval(i),14))

    for i in BAforSG_:
        for j in BAforSG_[i]:
            dbc_write.write('BA_ "GenSigStartValue" SG_ {} {} {};\n'.format(eval(i), j[0], j[1]))
    if CANFD_flag==1:
        dbc_write.write('BA_ "BusType" "CAN FD";\nBA_ "DBName" "CANFD";\n')

    prgprc = '5/5 读取并写入BA＿赋值信息结束\n'
    msg_queue.put(prgprc)


    '''读取并写入VAL'''
    for v in valuetable:
        if v[2] == '/':
            continue
        v_str = Change_valueTable(v[2])
        dbc_write.write('VAL_ {} {} {};\n'.format(eval(v[0]), v[1], v_str))
    prgprc = '写入valuetable结束\n生成target.dbc在当前目录\n-------over------'
    msg_queue.put(prgprc)

def DbcToExcel(msg_queue,dbc_pathT):
    prgprc = '初始化....'
    msg_queue.put(prgprc)
    def VAl_StyleChange(vab):
        messid_temp=vab.split(' ')[1]
        vab = vab.strip('\n').strip(';').strip(' ')
        list_return = []
        str_return = ''
        str_temp = ''
        isanum = 1
        spaceCon = 0
        point_return = 1
        vab = vab.split(' ')
        list_return.append(vab[2])
        for i in range(3, len(vab)):
            if vab[i].count('"') == 1:
                spaceCon += 1
            if spaceCon % 2 != 0:
                str_temp = str_temp + vab[i] + ' '
            if spaceCon % 2 == 0 and vab[i].count('"') == 1:
                str_temp = str_temp + vab[i]
                list_return.append(str_temp.strip('"'))
                str_temp = ''
            if spaceCon % 2 == 0 and (vab[i].count('"') == 0 or vab[i].count('"') == 2):
                list_return.append(vab[i].strip('"'))
        for i in range(1, len(list_return)):
            if isanum % 2 != 0:
                str_return = str_return + list_return[i] + ':'
            else:
                str_return = str_return + list_return[i].strip('"') + '\n'
            isanum = isanum + 1
        return [messid_temp,list_return[0], str_return.strip('\n')]

    msg_queue.put('1/5 文件检查OK')
    style_Lchange = xlwt.XFStyle()
    style_Lchange.alignment.wrap = 1
    source_dbc = open(dbc_pathT, 'r', encoding='ANSI')
    target_excel = xlwt.Workbook(encoding='ansi')
    target_sheet = target_excel.add_sheet('矩阵')
    Index_excel = ['NO.', 'Transmitter', 'Receiver', 'Signal_name', 'Signal_Description', 'Message_Name', 'Message_ID',
                   'Message_Type', 'Period(ms)', 'DLC', 'Msb', 'Lsb', 'Size(bit)', 'Byte_Order', 'Data_Type',
                   'Default_Initiaised_value', 'Alternative_Value', 'Factor', 'Offset', 'Value_Min_P',
                   'Value_Max_P', 'Unit', 'Coding']
    excellist_for_write = {}
    excellist_for_write_ALL={}
    for i in range(0, len(Index_excel)):
        target_sheet.write(0, i, Index_excel[i], style_Lchange)
    msg_queue.put('2/5 首行写入OK')
    messINFO_now = []
    dbc_lines = source_dbc.readlines()
    prgprc = 'hang'
    GenAttribute_def = {}
    GenAttribute_inialue = {}
    Message_ini = {}
    Signal_ini = {}
    Signal_valTable = {}
    for i in dbc_lines:
        if i == '\n':
            continue
        if i.count('BU_:') > 0:
            prgprc = 'start'
            continue
        if prgprc != 'hang':
            if i.split(' ')[0] == 'BO_':
                prgprc = 'mess'
                messINFO_now = i.replace('\n', '').split(' ')

                continue
            if i.strip(' ').split(' ')[0] == 'SG_':
                prgprc = 'signal'
                sigINFO_now = i.replace('\n', '').strip(' ').split(' ')
                excellist_for_write[sigINFO_now[1]] = \
                    [messINFO_now[4].strip('\n').strip(';'), sigINFO_now[7], sigINFO_now[1], '/'
                        , messINFO_now[2].strip(':'), hex(eval(messINFO_now[1])), ''
                        , 0, messINFO_now[3]
                        , ['/', sigINFO_now[3].split('|')[0]][sigINFO_now[3].split('@')[1].count('0') > 0]
                        , ['/', sigINFO_now[3].split('|')[0]][sigINFO_now[3].split('@')[1].count('1') > 0]
                        , sigINFO_now[3].split('|')[1].split('@')[0]
                        , ['Motorla', 'Inter'][sigINFO_now[3].split('@')[1].count('1') > 0]
                        , ['Signed', 'Unsigned'][sigINFO_now[3].split('@')[1].count('+') > 0]
                        , 0, '/'
                        , sigINFO_now[4].strip('(').strip(')').split(',')[0]
                        , sigINFO_now[4].strip('(').strip(')').split(',')[1]
                        , sigINFO_now[5].strip('[').strip(']').split('|')[0]
                        , sigINFO_now[5].strip('[').strip(']').split('|')[1]
                        , [sigINFO_now[6].strip(""), '/'][sigINFO_now[6] == '""']
                        , '/'
                     ]
                if messINFO_now[1] not in excellist_for_write_ALL:
                    excellist_for_write_ALL[messINFO_now[1]]={}
                    excellist_for_write_ALL[messINFO_now[1]].update(excellist_for_write)
                else:
                    excellist_for_write_ALL[messINFO_now[1]].update(excellist_for_write)
                excellist_for_write={}

            '''
            if i.split(' ')[0] == 'BO_TX_BU_':
                prgprc = 'BO_TX_BU'
                for j in excellist_for_write:
                    if excellist_for_write[j][5] == i.split(' ')[1]:
                        excellist_for_write[j][0] = i.split(' ')[3].strip(';')
            '''
            if i.split(' ')[0] == 'BA_DEF_':
                if i.count('DBName')>0 or i.count('BusType'):
                    continue

                prgprc = 'BA_DEF_'
                i = i.strip('\n').strip(';').split(' ')
                GenAttribute_def[i[3].strip('"')] = i[4:len(i) + 1]
                continue

            if i.split(' ')[0] == 'BA_DEF_DEF_':
                i = i.strip('\n').strip(';').split(' ')
                GenAttribute_inialue[i[1].strip('"')] = i[2].strip('"')
                prgprc = 'BA_DEF_DEF'
                continue

            if i.split(' ')[0] == 'BA_':
                prgprc = 'BA_'
                if i.count('BO_') > 0:
                    i = i.strip('\n').strip(';').split(' ')
                    Message_ini[i[3]] = [i[1].strip('"'), i[4]]
                if i.count('SG_')>0:
                    i = i.strip('\n').strip(';').split(' ')
                    Signal_ini[i[4]] = [i[1].strip('"'), i[5]]
                continue

            if i.split(' ')[0] == 'VAL_':
                prgprc = 'VAL_'
                j = VAl_StyleChange(i)
                Message_id=j[0]; Signal_name = j[1]
                excellist_for_write_ALL[Message_id][Signal_name][21] = j[2]
            if i.split(' ')[0] == 'CM_':
                prgprc = 'CM_'
    msg_queue.put('3/5 读取dbc OK')
    '''  #我也不知道为啥要注释这个，好像有用，不然我留着干嘛
    #下面对周期，方式，初始值进行初始化
    line_doing = 1
    col_doing  = 1
    for i in excellist_for_write:
        for k in GenAttribute_inialue:
            if k == 'GenMsgCycleTime':
                excellist_for_write[i][7] = GenAttribute_inialue[k]
            if k == 'GenMsgSendType':
                excellist_for_write[i][6] = GenAttribute_inialue[k]
            if k == 'GenSigStartValue':
                excellist_for_write[i][15] = GenAttribute_inialue[k]
   #下面对各类初始值进行赋值
    for i in Message_ini:
        for j in excellist_for_write:
            if eval(excellist_for_write[j][5]) == eval(i):
                if Message_ini[i][0] == 'GenMsgCycleTime':
                    excellist_for_write[j][7] = Message_ini[i][1]
                if Message_ini[i][0] == 'GenMsgSendType':
                    excellist_for_write[j][6] = Message_ini[i][1]
    for i in Signal_ini:
        if Signal_ini[i] == 'GenSigStartValue':
            excellist_for_write[i][15] = Signal_ini[i][1]
    '''
    msg_queue.put('4/5 值的初始化OK')
    '''下面开始遍历写入'''
    line_doing = 1
    for i in excellist_for_write_ALL:
        for j in excellist_for_write_ALL[i]:
            for k in range(1, len(excellist_for_write_ALL[i][j]) + 1):
                target_sheet.write(line_doing, k, excellist_for_write_ALL[i][j][k - 1])
            line_doing = line_doing + 1
    msg_queue.put('5/5 遍历写入OK')
    source_dbc.close()
    target_excel.save('target.xlsx')
    msg_queue.put('生成target.xlsx在本地目录\n-----over-----')

def DbcCombine(dbc_pathCom_1,dbc_pathCom_2, msg_queue):
    check_ID=0;  check_mess=0;  check_sig=0;                     #用来校验是否有冲突内容
    same_ID =0;  same_mess =0;  same_sig =0;
    if dbc_pathCom_1 == 'nofile' or dbc_pathCom_2 == 'nofile':
        msg_queue.put('Error: no file chosed')
    else:
        source_dbc1 = open(dbc_pathCom_1,'r',encoding='ANSI')
        source_dbc2 = open(dbc_pathCom_2,'r',encoding='ANSI')

        lines_dict1,ID_list1,mess_Name1,sig_Name1 = DBC_readAndstore(source_dbc1,0)       #flag ==0 表示以该dbc为基础
        lines_dict2,ID_list2,mess_Name2,sig_Name2 = DBC_readAndstore(source_dbc2,1)
        check_ID,sameID      = DBC_check(ID_list1, ID_list2)
        check_mess,same_mess = DBC_check(mess_Name1, mess_Name2)
        check_sig,same_sig   = DBC_check(sig_Name1, sig_Name2)
        msg_queue.put('1/3 dbc读取结束')

        if check_ID != '0':
            msg_queue.put('ID 存在冲突,例如{}'.format(same_ID))
        if check_mess != '0':
            msg_queue.put('name 存在冲突,例如{}'.format(same_mess))
        if check_sig != '0':
            msg_queue.put('sig 存在冲突,例如{}'.format(same_sig))
        if check_ID=='0' and check_mess == '0' and check_sig == '0':
            msg_queue.put('2/3 报文冲突监测完成')
            DBC_Combine_Write(lines_dict1,lines_dict2,msg_queue)
        else:
            source_dbc1.close()
            source_dbc2.close()
            lines_dict1={}
            lines_dict2={}
            msg_queue.put('3/3 文件关闭,消除冲突后重新使用')

def DBC_readAndstore(source_dbc,flag):
    lines_dbc = source_dbc.readlines()
    lines_list = []; ID_list=[] ;  mess_Name=[]; sig_Name=[]
    lines_dict = {'NS_':[],'BS_':[],'BU_':[],'message':[],'CM_':[],'BA_DEF_':[],'BA_DEF_DEF_':[],
                  'BA_':[],'VAL_':[]}
    flag_over = 0
    thisline_att = '' ;  thisline_id=''
    for line in lines_dbc:
        lines_list.append(line)
        if line.split(' ')[0] == 'NS_':
            thisline_att = 'NS_'
            lines_dict['NS_'] = ['NS_ :\n']
            continue
        if line.split(':')[0] == 'BS_':
            thisline_att = 'BS_'
            lines_dict['BS_']  = ['BS_:\n']
            continue
        if line.split(':')[0] == 'BU_':
            thisline_att = 'BU_'
            lines_dict['BU_']  = line
            continue
        if line.split(' ')[0] == 'BO_':
            thisline_att = 'message'
            thisline_id  = line.split(' ')[1]
            ID_list.append(line.split(' ')[1])
            mess_Name.append(line.split(' ')[2])
            lines_dict['message'].append(line)
            continue
        if line.split(' ')[0] == '':
            if line.split(' ')[1] == 'SG_':
                sig_Name.append(line.split(' ')[2])
        if line.split(' ')[0] == 'CM_':
            lines_dict['CM_'].append(line)
        if line.split(' ')[0] == 'BA_DEF_':
            thisline_att = 'BA_DEF_'
            lines_dict['BA_DEF_'].append(line)
        if line.split(' ')[0] == 'BA_DEF_DEF_':
            lines_dict['BA_DEF_DEF_'].append(line)
        if line.split(' ')[0] == 'BA_':
            if flag==1:
                if line.split(' ')[1]==["BusType"] or line.split(' ')[1]==["DBName"] :
                    continue
            lines_dict['BA_'].append(line)
        if line.split(' ')[0] == 'VAL_':
            lines_dict['VAL_'].append(line)

        if thisline_att == 'NS_':
            lines_dict['NS_'].append(line)

        if thisline_att == 'BS_':
            lines_dict['BS_'].append(line)

        if thisline_att == 'message':
            lines_dict['message'].append(line)
            continue

    return lines_dict,ID_list,mess_Name,sig_Name

def DBC_check(list1,list2):
    result='0'
    for value in list1:
        if value in list2:
            result=1
            break
    return result,value

def DBC_Combine_Write(dict1,dict2,msg_queue):
    target_dbc = open('target_Combine.dbc', 'a', encoding='ansi')
    target_dbc.close()
    os.remove('target_Combine.dbc')
    target_dbc = open('target_Combine.dbc', 'a', encoding='ansi')
    for part in dict1:
        if type(dict1[part]) ==str:
            target_dbc.write(dict1[part])

        elif part == 'message' or part == 'CM' or part == 'BA' or part == 'VAL':
            for i in dict1[part]:
                target_dbc.write(i)
            for j in dict2[part]:
                target_dbc.write(j)
            target_dbc.write('\n')
        else:
            for i in dict1[part]:
                target_dbc.write(i)
            target_dbc.write('\n')
    msg_queue.put('3/3 写入完成，关闭文件')
    target_dbc.close()













