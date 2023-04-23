import tkinter
import queue
import os
def Xml2cpal(xmlpath,chooseDir,msg_queue):
    if xmlpath == 'nofile' or chooseDir == 'nofile':
        msg_queue.put('choose a file/dir')
    else :
        chooseDir = chooseDir.replace('/',r'\\')+r'\\'
        sourceXml = open(xmlpath,'r',encoding='UTF-8')
        targetTxt = open('xmlTargetCPAL.txt','a')
        targetTxt.close()
        os.remove('xmlTargetCPAL.txt')
        targetTxt = open('xmlTargetCPAL.txt', 'a', encoding='UTF-8')
        thisgroup = ''
        msg_queue.put('1/3 读取xmL')
        for line in sourceXml:
            if 'testgroup title' in line:
                thisgroup = line.split('"')[1].split('_')[0]
            if 'capltestcase name' in line:
                targetTxt.write('///<{}>\n'.format(thisgroup))
                targetTxt.write('testcase {}()\n'.format(line.split('"')[1]))
                targetTxt.write('{\n')
                targetTxt.write('setLogFileName("Logging",'
                                '"{}{}_{{Time}}.asc"); \n'
                                'startLogging();\n'
                                'stopLogging();\n'.format(chooseDir,line.split('"')[1]))
                targetTxt.write('}\n')
        msg_queue.put('2/3 写入txt结束')
        targetTxt.close()
        sourceXml.close()
        msg_queue.put('3/3 关闭文件')







