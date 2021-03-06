# pyBurner
This GUI script automates 3DMax network render job resubmission if one of the render servers had failed.
## Description
Sometimes during render of a 3dMax animation on multiple servers, one of the render servers may fail the job. Then you need to resubmit the job with only frames that failed. You have to manually choose those frames and add them to render queue. I would prefer not to search failed frames manually. This script automates render job resubmission, so you have to just export job file from Backburner and then choose failed server. The result of the program is a `.bat` file, which being executed adds new job to the Backburner queue with all failed frames.

### Command line usage

To print all frames for each corresponding server in a job use `csv_parser.py` file:
 ```
python csv_parser.py neon9.txt
 ```

## Tkinter version description

`config.ini` file has options for:
* Render priority
* Path to the project folder with 3Ds Max scene
* 3Ds Max version (year)
* Render manager name or ip-address

If `config.ini` file is not found, new config file is generated with default values.

The result file structure is following:
`"C:\Program Files\Autodesk\3ds Max {year}\3dsmaxcmd.exe" "{path-to-max-file}.max" -frames:{comma separated frame numbers} -submit: {Backburner manager ip address} -jobname: {job_name}_{server_name} -priority:{1-100}`

### Installation and run

You can use Python 2 or Python 3 to run the app.

1. install [Python v3.6](https://www.python.org/downloads/release/python-361/)
2. `git clone git@github.com:movalex/pyburner.git` (you will probably have to install [Git for Windows](https://github.com/git-for-windows/git/releases/download/v2.13.1.windows.1/Git-2.13.1-64-bit.exe) first)
3. `py -3 pyburner.py` in script folder

### Standalone GUI application on Windows (py2exe)
While you can still start this script from command line, there's also standalone implementation. 
Keep in mind that latest Python 3 version that works with `py2exe` is 3.4.3.

* install [Python v3.4.3](https://www.python.org/downloads/release/python-343/)
* install py2exe `pip3 install py2exe`
* clone repository and open `pyburner` folder in command line: `git clone https://github.com/movalex/pyburner.git`
* use `py -3 setup.py` to build application
* check the `dist` folder in script location and run `pyburner.exe` file
* now you can use the script on any machine that has no python interpreter installed.

![](/../screenshots/images/screenshot.jpg "Main GUI")
![](/../screenshots/images/screenshot2.JPG "")

### Standalone Mac (Py2App)
You can also use the script as Mac application. I've added a lot of ugly hacks to make `tkinter` interface look almost the same on both Windows and OSX, completely for no reason.

![](/../screenshots/images/Screenshot%203.png "")

You can even build a standalone Mac application using [py2app](https://py2app.readthedocs.io/en/latest/). I have no idea if it is useful, since 3Ds Max and Backburner are both Windows applications...:)

## UI usage
1. Go to Backburner Queue Monitor and export report file to the Desktop by right clicking the job name.
You can try with [sample file](https://raw.githubusercontent.com/movalex/pyburner/master/neon9.txt) from this repository.
2. Launch the script and load that file by pressing <CTRL+O> or file->open
3. You will be provided with the list of servers involved in the render job. Choose one server that failed.
4. Click 'run' button (or press Space button), and choose .max scene you want to re-render. Default path to look for .max files is C:/userprofile/Documents/. You can override this in `config.ini` file in `path` option. For network path just use regular UNC (`\\{computer name}\sharedFolder\resource`) path.
5. If the `open result` check button is checked, the Explorer folder with .bat file will be opened. 
6. When you run this .bat file, new job should appear in Backburner monitor. Job name is inherited from original job plus failed server name (Ex: `neon_v09_renderserver1`)    
7. Since the script does not currently support multiple server submission, in case you have more than one server failed, just repeat steps 2-5. It is really fast after all.
8. `All Jobs` button shows each render server for the current job with corresponding frame numbers. This button is disabled until proper job file is loaded.

## TODO
* add tests as promised
* add `reload config` button to preferences
* save last used project folder path
* add `clear` button
