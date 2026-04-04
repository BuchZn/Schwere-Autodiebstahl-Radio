import subprocess
import random
import time
import threading

mp3_process = None
play_thread = None
stop_thread = False
play_lock = threading.Lock()  # Prevents race conditions when switching stations

FRAMES_PER_SEC = 48000 / 1152

time_old = 0

# Map of (folder_index, image_index) -> song path New
STATION_MAP = {
    (0, 1):  '/home/pi/audio/Blaine County Radio.mp3',
    (0, 2):  '/home/pi/audio/Non-Stop-Pop FM.mp3',
    (0, 3):  '/home/pi/audio/Blue Ark.mp3',
    (0, 4):  '/home/pi/audio/Channel X.mp3',
    (0, 5):  '/home/pi/audio/East Los FM.mp3',
    (0, 6):  '/home/pi/audio/Radio Los Santos.mp3',
    (0, 7):  '/home/pi/audio/Radio Mirror Park.mp3',
    (0, 8):  '/home/pi/audio/Rebel Radio.mp3',
    (0, 9):  '/home/pi/audio/Los Santos Rock Radio.mp3',
    (0, 10): '/home/pi/audio/Soulwax FM.mp3',
    (0, 11): '/home/pi/audio/Space 103.2.mp3',
    (0, 12): '/home/pi/audio/The Lowdown 91.1.mp3',
    (0, 13): '/home/pi/audio/Vinewood Boulevard Radio.mp3',
    (0, 14): '/home/pi/audio/West Coast Talk Radio.mp3',
    (0, 15): '/home/pi/audio/West Coast Classics.mp3',
    (0, 16): '/home/pi/audio/WorldWide FM.mp3',
    (0, 17): '/home/pi/audio/FlyLo FM.mp3',
    (0, 18): '/home/pi/audio/Los Santos Underground Radio.mp3',
    (0, 19): '/home/pi/audio/Blonded Radio.mp3',
    (0, 20): '/home/pi/audio/The Lab.mp3'
}

# Dictionary to store the duration of each MP3 file in seconds
mp3_durations = {
    '/home/pi/audio/Non-Stop-Pop FM.mp3': 10000, #C
    '/home/pi/audio/Blaine County Radio.mp3': 4892, #C
    '/home/pi/audio/Blue Ark.mp3': 4790, #C
    '/home/pi/audio/Channel X.mp3': 2827,#C
    '/home/pi/audio/East Los FM.mp3': 2465, #C
    '/home/pi/audio/Radio Los Santos.mp3': 6691, #C
    '/home/pi/audio/Radio Mirror Park.mp3': 9160, #C
    '/home/pi/audio/Rebel Radio.mp3': 3457, #C
    '/home/pi/audio/Los Santos Rock Radio.mp3': 9322, #C
    '/home/pi/audio/Soulwax FM.mp3': 2567, #C
    '/home/pi/audio/Space 103.2.mp3': 5653, #C
    '/home/pi/audio/The Lowdown 91.1.mp3': 4372, #C
    '/home/pi/audio/Vinewood Boulevard Radio.mp3': 3958, #C
    '/home/pi/audio/West Coast Talk Radio.mp3': 5617, #C
    '/home/pi/audio/West Coast Classics.mp3': 6978, #C
    '/home/pi/audio/WorldWide FM.mp3': 7232, #C
    '/home/pi/audio/FlyLo FM.mp3': 4298, #C
    '/home/pi/audio/Los Santos Underground Radio.mp3': 16731, #C
    '/home/pi/audio/Blonded Radio.mp3' : 6140, #C
    '/home/pi/audio/The Lab.mp3': 3456 #C
}

#Dict to save the Live Duration Frame of every Sation
random_durations = {
    '/home/pi/audio/Non-Stop-Pop FM.mp3': 0, 
    '/home/pi/audio/Blaine County Radio.mp3': 0, 
    '/home/pi/audio/Blue Ark.mp3': 0, 
    '/home/pi/audio/Channel X.mp3': 0,
    '/home/pi/audio/East Los FM.mp3': 0, 
    '/home/pi/audio/Radio Los Santos.mp3': 0, 
    '/home/pi/audio/Radio Mirror Park.mp3': 0, 
    '/home/pi/audio/Rebel Radio.mp3': 0,
    '/home/pi/audio/Los Santos Rock Radio.mp3': 0, 
    '/home/pi/audio/Soulwax FM.mp3': 0, 
    '/home/pi/audio/Space 103.2.mp3': 0, 
    '/home/pi/audio/The Lowdown 91.1.mp3': 0,
    '/home/pi/audio/Vinewood Boulevard Radio.mp3': 0,
    '/home/pi/audio/West Coast Talk Radio.mp3': 0,
    '/home/pi/audio/West Coast Classics.mp3': 0,
    '/home/pi/audio/WorldWide FM.mp3': 0, 
    '/home/pi/audio/FlyLo FM.mp3': 0, 
    '/home/pi/audio/Los Santos Underground Radio.mp3': 0,
    '/home/pi/audio/Blonded Radio.mp3' : 0, 
    '/home/pi/audio/The Lab.mp3': 0     
}

def init_random_duration():

    for path, total_l in mp3_durations.items():
        random_durations[path] = int(random.uniform(0, total_l) * FRAMES_PER_SEC)

# Update Duration so Stations feel like they are really playing in the Background
def update_duration(time_delta):
    # Wir brauchen selectedSong hier nicht mehr
    for path, current_frame in random_durations.items():
        # Vergangene Zeit in Frames umrechnen und addieren
        frames_passed = int(time_delta * FRAMES_PER_SEC)
        new_frame = current_frame + frames_passed
        
        # Maximale Frames für DIESEN spezifischen Sender berechnen
        max_frames = mp3_durations.get(path, 0) * FRAMES_PER_SEC
        
        # Wenn der Song zu Ende ist, fange wieder von vorne an
        if max_frames > 0:
            new_frame = new_frame % max_frames
            
        random_durations[path] = new_frame

def play_radio_thread(selectedSong, duration):
    global mp3_process
    global stop_thread

    while not stop_thread:
        #random_start_frame = int(random.uniform(0, duration) * FRAMES_PER_SEC)
        print(f"Playing {selectedSong} from frame {duration}")

        mp3_process = subprocess.Popen([
            'mpg123', '-q', '-a', 'hw:0,0', '--fuzzy', '-k', str(duration), selectedSong
        ])  
        song_duration = mp3_durations.get(selectedSong)
        sleep_time = song_duration - (duration / FRAMES_PER_SEC) - 2
        duration = 0

        # Sleep in small chunks so stop_thread can interrupt quickly
        steps = int(sleep_time * 10)
        for _ in range(steps):
            if stop_thread:
                break
            time.sleep(0.1)

        if mp3_process and mp3_process.poll() is None:
            mp3_process.terminate()


def play_radio(folder_index, image_index):
    global mp3_process
    global play_thread
    global stop_thread
    global time_old

    # FIX 2: Use a lock so rapid encoder turns can't spawn multiple threads at once
    with play_lock:
        selectedSong = STATION_MAP.get((folder_index, image_index))
        if selectedSong is None:
            print(f"Error: No station mapped for folder={folder_index}, index={image_index}")
            return

        # 1. Tell the old thread to stop
        stop_thread = True

        # 2. Kill the old audio process immediately
        if mp3_process and mp3_process.poll() is None:
            mp3_process.terminate()

        # 3. Wait briefly for the old thread to exit (non-blocking)
        if play_thread and play_thread.is_alive():
            play_thread.join(timeout=0.3)

        #Update other stations duration
        time_now = time.time()

        if(time_old == 0):
            elapsed_time = 0
            time_old = time.time()
        else:
            elapsed_time = time_now - time_old
        time_old = time_now

        update_duration(elapsed_time)



        #duration = mp3_durations.get(selectedSong)
        duration = random_durations.get(selectedSong)
        if duration is None:
            print(f"Error: Duration not found for {selectedSong}")
            return


        # 4. Start the new station
        stop_thread = False


        play_thread = threading.Thread(target=play_radio_thread, args=(selectedSong, duration), daemon=True)
        play_thread.start()