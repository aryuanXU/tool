

# -- 基于AUTOSAR 标准的时间同步自动化脚本生成
# -- 生成脚本基于CAPL 语言实现
# -- 20230421 V1版本
def TimeSYncCode_Generated():
    pass

#定义或确认外放参数
    SYNC_ID = 1
    diaReqID_phy = 0x701
    diaReqID_fun = 0x760
    dataDIDlist=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    systemCycle = 70
    canCycle    =70
    project_name = 'Time_xxx_xxx'
    capldll_dir =r'.\xxxx'
    includes_code  =  'includes \n' \
                      '{{\n' \
                      ' #pragma library("{}")\n' \
                      ' }}\n'.format(capldll_dir)
    variable_code  =  {'normal':
                      ' message {} Sync;\n' \
                      ' message {} Diag;\n' \
                      ' // VSync_Type  指的是，在Sync 报文中的type,VFup_Type 指的是在Fup 中的type'\
                      ' byte VSync_Type;\n' \
                      ' byte  VSync_CRC;\n' \
                      ' byte  VSync_Counter;\n' \
                      ' byte  VSync_Timedomain;\n' \
                      ' byte  VSync_OVS;  //实际无\n' \
                      ' byte  VSync_SGW;  //实际无\n' \
                      ' byte  VSync_Res;\n' \
                      ' qword VSync_Time;\n' \
                      ' \n' \
                      ' byte  VFup_Type;\n' \
                      ' byte  VFup_CRC;\n' \
                      ' byte  VFup_Counter;\n' \
                      ' byte  VFup_Timedomain;\n' \
                      ' byte  VFup_OVS;\n' \
                      ' byte  VFup_SGW;\n' \
                      ' byte  VFup_Res;\n' \
                      ' qword VFup_Time;\n' \
                      ' qword VSync_Alltime;\n' \
                      ' msTimer SyncTimer, FupTimer, From0Timer;//fup之后开始from0计时器计时' \
                      ' byte DataDIDList[16];\n' \
                      ' qword AutosartimestampS[6];\n' \
                      ' qword AutosartimestampN[6];\n' \
                      ' qword Autosartimestamp[6];\n' \
                      ' dword noSync_AutosartimestampS;\n' \
                      ' dword noSync_AutosartimestampN;\n' \
                      ' int SYNcycle; int FUPcycle; int SYScycle; //2条报文周期以及系统周期 \n' \
                      ' \n' \
                      ' int Count_counter;         // 实现counter滚动以及不滚动\n' \
                      ' int Count_radarM;          // 发出同步报文后的雷达指定报文接收器\n' \
                      ' int Flag_waitForRadar;     // 该Flag标识是否FUP发送结束，进入等待雷达报文状态\n' \
                      ' byte  ADD_CRC_Sync;        // 该valid附加给syncCRC形成错误CRC\n' \
                      ' byte  ADD_CRC_Fup;         // 该valid附加给fupCRC形成错误CRC\n' \
                      ' byte  Valid_Syncoutput;    // 该valid标识了全局Sync报文是否正常发送\n' \
                      ' byte  Valid_Fupoutput;\n'.format(SYNC_ID,),
                      're1':' 预留1 ',
                      're2':' 预留2 ',
                      're3':' 预留3'}




    project_can = open('{}.txt'.format(project_name),'a',encoding= 'utf-8')


def Cycle_Analysis():
    pass













