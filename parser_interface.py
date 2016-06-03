from __future__ import print_function
import os
import sys
import csv
import socket
import platform
import subprocess

if sys.version_info[0] == 3:
    from tkinter import filedialog
    import tkinter as tk
else:
    import tkFileDialog as filedialog
    import Tkinter as tk


def trunkate_file(file):
    try:
        f = open(file, 'r+')
        f.truncate()
    except FileNotFoundError:
        pass

PRIORITY = 100
VERSION = 2014

class MyTextSettings(tk.Text):

    def setFrames(self, frame):
        self.insert(tk.END, frame)
        self.see(tk.END)

    def setText(self, text):
        self.insert(tk.END, text+'\n')
        self.see(tk.END)

    def clear(self, *args):
        self.delete("1.0", tk.END)
        
    def clear_help(self, *args):
        self.clear()
        self.setText('Choose "File --> Open" or press "CTRL+o"')
        self.setText('to open .csv or .txt file')
        

class MainApplication(tk.Tk):
    """main GUI"""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('+300+100')
        self.title('CSV Parser')
        
        # text area frame
        frame1 = tk.Frame(self)
        scrollbar = tk.Scrollbar(frame1)
        self.text = MyTextSettings(frame1, width=52, height=20,
                                   wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.config(command=self.text.yview)
        frame1.grid(row=0, column=0, sticky='w')
        
        # buttons area frame
        frame2 = tk.Frame(self) 
        self.L0 = tk.Label(frame2)
        self.L0.grid(row=0, column=0, columnspan=3, sticky='we')
        self.L1 = tk.Label(frame2, text='Enter server number:')
        self.L1.grid(row=1, column=0, sticky='w')
        self.L2 = tk.Label(frame2, width=8, text='')
        self.L2.grid(row=1, column=1)
        self.L2.grid_propagate(False)
        self.entry = tk.Entry(frame2, width=7)
        self.entry.grid(row=1, column=2, sticky='w', padx=2)

        #offset entry size for mac/win interface consistency
        offset_size = None
        if platform.system() == 'Windows':
            offset_size = 15 #stupid hardcode
            self.entry.config(width=offset_size)

        button1 = tk.Button(frame2, text='submit', command=self.get_server_entry)
        button1.grid(row=1, column=3, sticky='w')
        button1.config(width=offset_size)
        self.bind('<Return>', self.get_server_entry)
        self.button2 = tk.Button(frame2, text='run', command=self.run_app)
        self.button2.grid(row=2, column=2, columnspan=2, sticky='we')
        self.bind('<Control-r>', self.run_app)
        self.var = tk.IntVar()
        self.var.set(1)
        self.checkbutton1 = tk.Checkbutton(frame2, text='open result',
                                           variable=self.var)
        self.checkbutton1.grid(row=2, column=0, sticky='w')
        button_clear = tk.Button(frame2, text='clear', command=self.cleanup)
        button_clear.grid(row=3, column=2,columnspan=2, sticky='we')
        button_clear.config()
        button3 = tk.Button(frame2, text='close', command=self.quit)
        button3.grid(row=4, column=2, columnspan=2, sticky='we')
        frame2.grid(row=1, column=0, sticky='we', padx=(5,0))

        #file menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        self.config(menu=menubar)
        filemenu.add_command(label='Open',
                             command=self.csv_open,
                             accelerator="Ctrl+O")
        filemenu.add_command(label='Preferences', 
                             command=self.show_pref)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', 
                             command=self.quit,
                             accelerator='Ctrl+Q')
        self.bind("<Control-o>", self.csv_open)
        self.bind("<Control-q>", self.quit)
        menubar.add_cascade(label='File', menu=filemenu)

        #default values
        self.os_name = platform.system()
        self.file_contents_list = []
        self.job_name = False
        self.selected_server = False
        self.max_version = '\"C:\\Program Files\\Autodesk\\3ds Max {}\\3dsmaxcmd.exe\"'.format(VERSION)
        self.text.clear_help()
        self.servers = []
        self.maxfilepath= ''

    def cleanup(self):
        self.L2.config(text='')
        self.entry.delete("0", tk.END)
        self.text.clear_help()
        self.restore_defaults()

    def restore_defaults(self):
        self.job_name = False
        self.selected_server = False
        self.file_contents_list = []
        self.servers = []

    def csv_open(self, *args):
        self.restore_defaults()
        self.text.clear()
        the_csv_file = filedialog.askopenfilename(
                        initialdir='{}/Desktop'.format(os.path.expanduser('~')),
                        filetypes=(('Text File', '*.txt'),
                                   ('CSV file', '*.csv'),
                                   ('All Files', '*.*')),
                        title='Choose a file')
        if the_csv_file:
            with open(the_csv_file, 'r') as file:
                file_contents = csv.reader(file, dialect='excel-tab')
                for elem in file_contents:
                    self.file_contents_list.append(elem)
            for i in self.file_contents_list:
                if len(i) == 1 and i[0][:4] == "Job:":
                    job_name = (i[0].split())
                    self.job_name = job_name[1]
                    self.text.setText('Job name: {}'.format(self.job_name))
                elif len(i) == 5 and i[4] != "Server":
                    self.servers.append(i[4])
                else:
                    pass
            sorted_servers = sorted(set(self.servers))
            self.text.setText("Found {} servers in file:".format(
                              len(set(self.servers))))
            for num, serv in enumerate(sorted_servers):
                self.text.setText('{}) {}'.format(num, serv))
            self.L2.config(text='0-{}'.format(
                           len(sorted_servers)-1))
            self.entry.delete("0", tk.END)
            self.entry.focus()
        else:
            self.text.clear_help()
            self.L2.config(text='')

    def get_server_entry(self, *args):
        self.server_num = self.entry.get()
        try:
            if int(self.server_num) >= 0:
                self.selected_server = sorted(set(
                                       self.servers))[int(self.server_num)]
                self.text.setText('you\'ve selected server #{}'.format(
                                   self.server_num))
                self.text.setText('\'{}\''.format(self.selected_server))
                self.text.setText(r'Now press "run" button (CTRL+r) to choose MAX file')
                self.button2.focus()
            else:
                self.text.setText('enter positive number, dammit!')
        except (ValueError, IndexError) :
            self.text.setText('enter correct number, please')

    def return_frames(self):
        for _line in self.file_contents_list:
            try:
                if _line[4] == self.selected_server:
                    if _line[2] == "00000":
                        frame = _line[2][:1]
                    else:
                        frame = _line[2].lstrip("0")
                    yield frame
                else:
                    pass
            except IndexError:
                pass

    def choose_max_file(self):
        openmaxfile = filedialog.askopenfilename(
                  initialdir=r'\\MEIJIN-3DMAX\Projects\TestCMD_Render\scenes',
                  title='Choose MAX file')
        self.maxfilepath = os.path.normpath(openmaxfile)
        return self.maxfilepath

    def add_quotes(self, txt):
        return '"{}"'.format(txt)
        
    def open_result(self, folder):
        # show the bat-file folder in Windows Explorer or Finder
        if self.os_name == 'Darwin':
            subprocess.Popen(['open', folder])
        elif self.os_name == 'Windows':
            subprocess.Popen('explorer /open, {}'.format(folder))
        else:
            pass

    def run_app(self, *args):
        if self.job_name and self.selected_server:
            self.text.setText('These frames will be re-rendered:')
            for frame in self.return_frames():
                self.text.setFrames('{}, '.format(frame))
            self.text.setFrames('\n')
            self.make_bat(self.choose_max_file())
            if self.var.get() == 1:
                self.text.setText('\nOpening folder...')
                self.open_result(os.path.split(self.maxfilepath)[0])
                self.var.set(0) # uncheck button to prevent multiple windows
            else:
                pass
        elif not self.job_name: 
            self.text.setText("You should select jobs file first")
        elif not self.selected_server:
            self.text.setText("Enter server number and submit!")

    def make_bat(self, maxfilepath):
        quoted_max_file = self.add_quotes(self.maxfilepath)
        max_folder, max_file = os.path.split(self.maxfilepath)
        filename, _ = os.path.splitext(max_file)
        bat_file = os.path.join(max_folder, '{}_rerender.bat'.format(filename))
        trunkate_file(bat_file)
        with open(bat_file, 'a') as bat:
            print(self.max_version, quoted_max_file, file=bat, end=' ')
            print('-frames:', file=bat, end='')
            for frame in self.return_frames():
                print(frame, file=bat, end=',')
            print(' -submit:', socket.gethostbyname('2renderingserv'),
                  file=bat, end='')
            print(' -jobname: {}_{}_rerender'.format(self.job_name,
                                                     self.selected_server),
                                                     file=bat, end='')
            print(' -priority:{}'.format(PRIORITY), file=bat)
            bat.close()
        self.text.setText('Done!\nPlease, check "{}" file at {}'.format(
                          os.path.split(bat_file)[1], max_folder))
        self.entry.focus()

    def show_pref(self):
        preftext = "Here\'ll be preferences\nfor MAX version,\npriority slider,\nbat-file save folder settings"
        pref = tk.Toplevel()
        pref.geometry('400x250+780+100')
        pref.title('Preferences')
        info_label = tk.Label(pref, text=preftext, justify=tk.CENTER)
        info_label.pack(side='top', padx=10, pady=50)

    def quit(self, *args):
        sys.exit(0)


if __name__ == '__main__':
    app = MainApplication()
    app.resizable(width=tk.FALSE, height=tk.FALSE)
    app.mainloop()
