import tkinter.filedialog
import ExcelToDbc,xlrd,os,IniCompare
import threading
import time
import queue
from tkinter import *
from tkintertable import TableCanvas,TableModel
'this is 3stchange'
colnum   =  1.0
dbc_pathT= 'nofile'
mtx_pathT= 'nofile'
asc_path = 'nofile'
dbc_path = 'nofile'

class mainGUI(object):
    msg_queue = None

    def __init__(self):
        self.win = Tk()
        self.win.title("转换工具 EXV1.1")
        self.win.config(bg='#F5F5F5')
        self.win.geometry('700x600')
        self.interface()
        self.msg_queue = queue.Queue()
    def interface(self):
        self.Label0          = Label (self.win, text = '----------BDC——EXCEL互转模块----------')
        self.Button0         = Button(self.win, text = ' >CAN转  ',    command=self.dbc_start,  bg='#87CEEB')
        self.Button1         = Button(self.win, text = ' >CANFD转 ',   command=self.dbcFD_start,bg='#87CEEB')
        self.Button2         = Button(self.win, text = ' >转excel ',   command=self.excel_start,bg='#87CEEB')
        self.Button_opendbcT = Button(self.win, text = 'Open Mtx',     command=self.openmtxT)
        self.Button_openmtxT = Button(self.win, text = 'Open dbc',     command=self.opendbcT)
        self.Label_dbcpathT  = Label (self.win, text =' mtx_path')
        self.Label_mtxpathT  = Label (self.win, text = 'dbc_path')
        self.tex_dbcpathT    = Text  (self.win, width=30, height=4)
        self.tex_mtxpathT    = Text  (self.win, width=30, height=4)
        self.Label0.           place(x=50, y=10)
        self.Label_dbcpathT.   place(x=10, y=40)
        self.Label_mtxpathT.   place(x=10, y=120)
        self.tex_mtxpathT  .   place(x=70, y=50)
        self.tex_dbcpathT  .   place(x=70, y=120)
        self.Button0       .   place(x=300,y=80)
        self.Button1       .   place(x=390,y=80)
        self.Button2       .   place(x=300,y=150)
        self.Button_opendbcT.  place(x=300,y=50)
        self.Button_openmtxT.  place(x=300,y=120)

        self.Label1          = Label(self.win, text = '会对比当前路径下的blf文件和')
        self.Label_dbcpathe  = Label(self.win, text='.dbc_path')
        self.Label_sp        = Label(self.win,text ='-----------initial/rolling/checksum简单对比-----------')
        self.Button_opendbc  = Button( self.win, text =' Open DBC ',  command=self.opendbc_start)
        self.Button_iniCompare= Button(self.win, text =' >>Next   ',  command=self.iniCompare_start)
        self.text_dbcpath    = Text(self.win, width=30, height=4)
        self.Label_dbcpathe.   place(x=10, y=270)
        self.Label_sp.         place(x=50, y=250)
        self.text_dbcpath.     place(x=70, y=270)
        self.Button_opendbc.   place(x=300,y=280)
        self.Button_iniCompare.place(x=300,y=350)
        self.text_write      = Text(self.win, width=30, height=30)
        self.text_write.       place(x=480, y=40)

    def event_print(self,root):
        global colnum
        if self.msg_queue.empty()==False:
            self.text_write.insert(colnum, self.msg_queue.get() + '\n')
            colnum+=2
        root.after(100,self.event_print,root)
    def dbc_start(self):
        self.T1=threading.Thread(target=ExcelToDbc.ExcelToDbc(self.msg_queue,0,mtx_pathT))
        self.T1.setDaemon(True)
        self.T1.start()
        self.event_print(self.win)
    def excel_start(self):
        self.T2=threading.Thread(target=ExcelToDbc.DbcToExcel(self.msg_queue,dbc_pathT))
        self.T2.setDaemon(True)
        self.T2.start()
        self.event_print(self.win)
    def dbcFD_start(self):
        self.T2=threading.Thread(target=ExcelToDbc.ExcelToDbc(self.msg_queue,1))
        self.T2.setDaemon(True)
        self.T2.start()
        self.event_print(self.win)
    def opendbc_start(self):
        self.T5=threading.Thread(target=self.opendbc)
        self.T5.setDaemon(True)
        self.T5.start()
        self.event_print(self.win)
    def iniCompare_start(self):
        self.T6 = threading.Thread(target=IniCompare.iniCompare( dbc_path, self.msg_queue))
        self.T6.setDaemon(True)
        self.T6.start()
        self.event_print(self.win)
    def opendbc(self):
        global dbc_path
        dbc_path = tkinter.filedialog.askopenfilename(title='selet a file ', initialdir='./',
                                                      filetypes=(('dbc', '*.dbc'),))
        self.text_dbcpath.insert(1.0, dbc_path)
    def opendbcT(self):
        global dbc_pathT
        dbc_pathT=tkinter.filedialog.askopenfilename(title='selet a file ', initialdir='./',
                                                    filetypes=(('dbc', '*.dbc'),))
        self.tex_dbcpathT.insert(1.0, dbc_pathT)
    def openmtxT(self):
        global mtx_pathT
        mtx_pathT = tkinter.filedialog.askopenfilename(title='selet a file ', initialdir='./',
                                                      filetypes=(('XLSX 工作表', '*.xlsx'),))
        self.tex_mtxpathT.insert(1.0, mtx_pathT)
mainWin=mainGUI()
mainWin.win.mainloop()





