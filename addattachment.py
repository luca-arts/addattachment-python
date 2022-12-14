"""
entry file for the addattachment project
In this file, we'll:
1. have a GUI for entering player name?
2. setup of directory structure
3. three different processes for capturing data:
    - open the websocket towards unity
    - start capturing the EEG datastream + insert markers based on LSL markers
    - capture OSC messages of Emotibit Oscilloscope

We'll try to make an executable of this project using PyInstaller
"""
import asyncio
from datetime import datetime

from brainflow import BoardIds

from EEG.brainflow_get_data import EEG
from LSL.LSL_ReceiveData import LSLReceptor
from Player.PlayerSession import PlayerSession
from utils.GUI import GUI
from utils.utils import *
from websocket.WebSocketServer import startWsServer


def stop_all(websocket, eeg, gsr):
    eeg.stop_eeg()


if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
    # load the config file
    config = load_config(Path(Path.cwd() / "conf.yaml"))
    # make a player object to keep track of variables
    player = PlayerSession(gui.get_results(), datetime.now().strftime("%Y_%m_%d__%H_%M"))
    # create the folder structure to capture the different datastreams
    root_data_path = create_folder_structure(player.playtime, config)
    # create a config file keeping track of all settings for that child
    player.create_player_conf(location=root_data_path, file_name="player_config.json")
    # check if an LSL stream is running
    lsl = LSLReceptor(value="Markers")
    while not lsl.is_running():
        continue
    # open EEG stream and stream towards EEG folder
    eeg = EEG(
        config=config,
        root_data_path=root_data_path,
        board_id=BoardIds.CYTON_BOARD
    )
    eeg.launch_eeg()

    # open websocket and stream data to folder websocket (separate files for EOG data?)
    websocket_data = [
        {"name": player.name},
        {"contingency": player.contingency}
    ]
    try:
        asyncio.run(startWsServer(params=websocket_data, ip="localhost", port=8081))
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("stopped by keyboard")
        stop_all(eeg=eeg)
        pass
