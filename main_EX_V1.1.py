import tkinter.filedialog

import ExcelToDbc,xlrd,os
import threading
import time
import queue
from tkinter import *
from tkintertable import TableCanvas,TableModel
colnum = 1.0
asc_path = 'nofile'
dbc_path = 'nofile'

class GUI(object):
    msg_queue = None

    def __init__(self):
        self.win = Tk()
        self.win.title("转换工具 EXV1.1")
        self.win.geometry('700x600')
        self.interface()
        self.msg_queue = queue.Queue()
    def interface(self):
        self.Label0=Label(self.win, text = '-------BDC——EXCEL互转模块-------')
        self.Label1=Label(self.win, text = '会对比当前路径下的blf文件和')
        self.Label_ascpath = Label(self.win, text ='.csv_path')
        self.Label_dbcpathe= Label(self.win, text='.dbc_path')
        self.Label_sp=Label(self.win,text ='---------INI_MIN_MAX_对比模块---------')

        self.Button0 = Button( self.win, text ='   To DBC   ',       command=self.dbc_start)
        self.Button1 = Button( self.win, text = ' To DBC_CANFD ',    command=self.dbcFD_start)
        self.Button2 = Button( self.win, text = '  To EXCEL ',       command=self.excel_start)
        self.Button_openasc = Button( self.win, text =' Open ASC ',   command=self.openasc_start)
        self.Button_opendbc = Button( self.win, text = ' Open DBC ', command=self.opendbc_start)
        self.Button_iniCompare=Button(self.win,text='IniCompare',    command=self.iniCompare_start)

        self.text1=Text(self.win,width=40,height=30)
        self.text_ascpath=Text(self.win, width=30, height=4)
        self.text_dbcpath=Text(self.win,width=30,  height=4)
        self.text_2=Text(self.win,width=40,height=30)

        self.Label0. place(x=50, y=10)
        self.Label_ascpath. place(x=10, y=170)
        self.Label_dbcpathe.place(x=10, y=230)
        self.Label_sp.place(x=50,y=150)

        self.text1.  place(x=400, y=40)
        self.text_ascpath.place(x=70, y=170)
        self.text_dbcpath.place(x=70, y=230)

        self.Button0.place(x=50, y=40)
        self.Button1.place(x=150,y=40)
        self.Button2.place(x=50, y=80)
        self.Button_openasc.place(x=300, y=180)
        self.Button_opendbc.place(x=300,y=240)
        self.Button_iniCompare.place(x=200,y=310)

    def event_print(self,root):
        global colnum
        if self.msg_queue.empty()==False:
            self.text1.insert(colnum,self.msg_queue.get()+'\n')
            colnum+=2
        root.after(100,self.event_print,root)

    def dbc_start(self):
        self.T1=threading.Thread(target=ExcelToDbc.ExcelToDbc(self.msg_queue,0))
        self.T1.setDaemon(True)
        self.T1.start()
        self.event_print(self.win)
    def excel_start(self):
        self.T2=threading.Thread(target=ExcelToDbc.DbcToExcel(self.msg_queue))
        self.T2.setDaemon(True)
        self.T2.start()
        self.event_print(self.win)
    def dbcFD_start(self):
        self.T2=threading.Thread(target=ExcelToDbc.ExcelToDbc(self.msg_queue,1))
        self.T2.setDaemon(True)
        self.T2.start()
        self.event_print(self.win)
    def openasc_start(self):
        self.T4=threading.Thread(target=self.openasc)
        self.T4.setDaemon(True)
        self.T4.start()
        self.event_print(self.win)
    def opendbc_start(self):
        self.T5=threading.Thread(target=self.opendbc)
        self.T5.setDaemon(True)
        self.T5.start()
        self.event_print(self.win)


    def iniCompare_start(self):
        self.T6 = threading.Thread(target=ExcelToDbc.iniCompare(asc_path, dbc_path, self.msg_queue))
        self.T6.setDaemon(True)
        self.T6.start()
        self.event_print(self.win)

    def openasc(self):
        global asc_path

        asc_path=tkinter.filedialog.askopenfilename(title='selet a file ', initialdir='./',
                                                    filetypes=(('ASSCII Logging File', '*.asc'),))
        self.text_ascpath.insert(1.0, asc_path)

    def opendbc(self):
        global dbc_path

        dbc_path = tkinter.filedialog.askopenfilename(title='selet a file ', initialdir='./',
                                                      filetypes=(('dbc', '*.dbc'),))
        self.text_dbcpath.insert(1.0, dbc_path)



a=GUI()
b=GUI()
a.win.mainloop()


