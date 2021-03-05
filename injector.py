import threading
import time
import PySimpleGUI as sg
import psutil
from pathlib import Path
import subprocess


def is_running(process_name):
    running = False
    for proc in psutil.process_iter():
        if process_name in proc.name():
            running = True
            break
    return running


def the_thread(window: sg.Window, logtext, values, gtav_exe, dll_name):
    injected = False
    while not injected:
        if is_running(gtav_exe):
            logtext += f"\n{gtav_exe} is running..."
            window["log"].update(logtext)
            delay = int(values["delay"])
            logtext += f"\nInjecting DLL in {delay} seconds..."
            window["log"].update(logtext)
            time.sleep(delay)
            inj_path = Path("Injector.exe").resolve()
            window["log"].update(logtext)
            inj_output = subprocess.run([inj_path, "--process-name", gtav_exe, "--inject", dll_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
            inj_output_out = inj_output.stdout.decode("UTF-8")
            logtext += f"\n{inj_output_out}"
            window["log"].update(logtext)
            injected = True
            window["start"].update(disabled=False)


def main():
    delay = 10
    gta_path = ""
    dll_name = "GTAO_Booster.dll"
    gtav_exe = "GTA5.exe"
    play_gta = "PlayGTAV.exe"

    if Path.exists(Path("settings.ini")):
        with open("settings.ini", 'r') as file:
            content = file.readlines()
            for line in content:
                if "[GTA5_LOC]=" in line:
                    gta_path = line.split("=")[1]
                if "[DELAY]=" in line:
                    delay = int(line.split("=")[1])
                if "[DLL]=" in line:
                    dll_name = line.split("=")[1]

    sg.theme('Dark')
    layout = [
        [sg.Text('Select PlayGTAV.exe:', size=(16,1)), sg.Input(gta_path, key="gta_exe"), sg.FileBrowse(file_types=((play_gta, play_gta),))],
        [sg.Text('Select DLL:', size=(16,1)), sg.Input(dll_name, key="dll"), sg.FileBrowse(file_types=(("", "*.dll"),))],
        [sg.Text('Injection Delay:', size=(16,1), tooltip="Delay to allow GTA to start & decrypt memory. Depending on PC performance and storage media you can decrease/increase this value."), sg.Input(delay, size=(5, 1), enable_events=True, tooltip="Delay to allow GTA to start & decrypt memory. Depending on PC performance and storage media you can decrease/increase this value.", key="delay")],
        [sg.Multiline(size=(70, 12), enable_events=True, key="log", autoscroll=True, disabled=True)],
        [sg.Button('START GTAV & Inject DLL', key="start", disabled=False), sg.Button('EXIT', key="exit", button_color=("white", "red"))],
        [sg.Text('© ThatOldGrumpyMan', size=(16, 1))],
    ]

    window = sg.Window('GTAV Auto DLL Injector', layout, finalize=True)

    if not Path.exists(Path("Injector.exe")):
        logtext = "Injector.exe is missing! Place it in the same directory as this file!\nInjector.exe is required to inject DLL in process.\nGet it here: https://github.com/nefarius/Injector\nRestart application when done."
        window["log"].update(logtext)
        window["start"].update(disabled=True)

    if is_running(gtav_exe):
        logtext = "GTA V is already running! Close it and restart this application!"
        window["log"].update(logtext)
        window["start"].update(disabled=True)

    while True:
        event, values = window.read()

        try:
            delay = str(values["delay"])
        except TypeError:
            delay = str(delay)
        if len(delay) > 0 and delay[0] not in ('123456789'):
            window["delay"].update(values["delay"][:-1])
        if len(delay) > 0 and delay[-1] not in ('0123456789'):
            window["delay"].update(values["delay"][:-1])
        if len(delay) > 2:
            window["delay"].update(values["delay"][:-1])

        if event == "start":
            logtext = ""
            window["log"].update(logtext)
            window["start"].update(disabled=True)
            gta_path = Path(str(values["gta_exe"]).strip("\n")).resolve()

            try:
                logtext = "Starting GTA V..."
                window["log"].update(logtext)
                subprocess.Popen([gta_path])
            except WindowsError:
                logtext += "\nInvalid GTA Path!"
                window["log"].update(logtext)
                window["start"].update(disabled=False)
                continue

            with open("settings.ini", 'w') as file:
                file.write("[GTA5_LOC]=" + str(values["gta_exe"]) + "\n" + "[DELAY]=" + str(values["delay"]) + "\n" + "[DLL]=" + str(values["dll"]))

            logtext += "\nWaiting for GTA V to start..."
            window["log"].update(logtext)

            dll_name = Path(str(values["dll"]).strip("\n")).resolve()

            threading.Thread(target=the_thread, args=(window, logtext, values, gtav_exe, dll_name), daemon=True).start()

        if event == "exit" or event == sg.WIN_CLOSED:
            break
    window.close()


if __name__ == '__main__':
    main()