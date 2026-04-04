import time
import signal
from PIL import Image
import struct
from RPi import GPIO
from PlayRadio import play_radio, init_random_duration
import threading




CLK  = 5
DT = 6
SW = 26


GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW,GPIO.IN , pull_up_down=GPIO.PUD_DOWN)


BLC_Radio = "./img/BLC.jpeg"
Nonstopp = "./img/NonStopPop.jpg"
BlueArk = "./img/BlueArk.jpeg"
ChannelX = "./img/ChannelX.jpeg"
EastLostFM = "./img/EastLostFm.jpeg"
EastLosantos = "./img/EastLosantos.jpeg"
RadioMirrow = "./img/RadioMirrow.jpeg"
RebelRadio = "./img/RebelRadio.jpeg"
RockRadio = "./img/RockRadio.jpeg"
SoulwaxFM = "./img/SoulwaxFM.jpeg"
SpaceFM = "./img/SpaceFM.jpeg"
Thelowlay = "./img/Thelowlay.jpeg"
Vineyard = "./img/Vineyard.jpeg"
WCTRradio = "./img/WCTR.jpeg"
WestCoastClassic = "./img/WCclassics.jpeg"
WorldwideFM = "./img/WorldWideFM.jpg"
FlyloFM = './img/FlyloFM.jpeg'
LosU = './img/LosSantosU.jpg'
Lap = './img/LapR.jpg'
Blonde = './img/Blonded_Radio.jpeg'
Loading = './img/Loading_Screen.jpg'


#Rotary Encoder Conf
counter = 0
clkLastState = GPIO.input(CLK)   # Initial read of CLK pin
clkState = 0
delayTime = 0.02
dtState = 0
swState = 0
image_index = 1

def create_buffer(img_path):
    img = Image.open(img_path).convert("RGB")
    img = img.resize((240, 240))
    pixels = img.load()
    
    # Erstellen einen leeren Daten-Puffer
    buffer = bytearray()
    
    # Jeden einzelnen Pixel durchgehen und in den Puffer packen
    for y in range(240):
        for x in range(240):
            r, g, b = pixels[x, y]
            
            # Die Farben für das Display in das 16-Bit Format (RGB565) umrechnen
            color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            
            # Die 2 Bytes des Pixels an den Puffer anhängen
            buffer.extend(struct.pack('<H', color))

    return buffer

blc = create_buffer(BLC_Radio)
nonstop = create_buffer(Nonstopp)
blueA = create_buffer(BlueArk)
CHx = create_buffer(ChannelX)
ELSfm = create_buffer(EastLostFM)
Es = create_buffer(EastLosantos)
Rm = create_buffer(RadioMirrow)
RebelR = create_buffer(RebelRadio)
RockR = create_buffer(RockRadio)
Soulwax = create_buffer(SoulwaxFM)
Space = create_buffer(SpaceFM)
Lowlay = create_buffer(Thelowlay)
Vn = create_buffer(Vineyard)
WTCr = create_buffer(WCTRradio)
WSc = create_buffer(WestCoastClassic)
WWfm = create_buffer(WorldwideFM)
Flfm = create_buffer(FlyloFM)
LosUfm = create_buffer(LosU)
LapB = create_buffer(Lap)
BlondeB = create_buffer(Blonde)
Loading_S = create_buffer(Loading)


def write_to_lcd(buffer):
    # Create an internal function for the thread to run
    def _write():
        try:
            with open("/dev/fb1", "wb") as fb:
                fb.write(buffer)
            print("Bild ist auf dem Display!")
        except Exception as e:
            print(f"LCD Error: {e}")

    # Start it in the background
    lcd_thread = threading.Thread(target=_write)
    lcd_thread.start()

encoder_steps = 0
# Updated callback logic
def ausgabeFunktion(channel):
    global image_index, clkLastState, encoder_steps
    
    # Read current state of CLK
    current_clk = GPIO.input(CLK)
    
    # Only act if the state has actually changed
    if current_clk != clkLastState:
        if GPIO.input(DT) != current_clk:
            encoder_steps += 1
        else:
            encoder_steps -= 1

        # Erst bei jedem 2. Schritt den Index ändern
        if abs(encoder_steps) >= 2:
            if encoder_steps > 0:
                image_index += 1
            else:
                image_index -= 1
            
            encoder_steps = 0  # zurücksetzen

            if image_index > 21: image_index = 1
            if image_index < 1:  image_index = 21


            if(image_index == 1):
                write_to_lcd(blc)
                play_radio(0, 1)
            elif((image_index > 1) and (image_index <= 2)):
                write_to_lcd(nonstop)
                play_radio(0, 2)
            elif((image_index > 2) and (image_index <= 3)):
                write_to_lcd(blueA)
                play_radio(0, 3)
            elif((image_index > 3) and (image_index <= 4)):
                write_to_lcd(CHx)
                play_radio(0, 4)
            elif((image_index > 4) and (image_index <= 5)):
                write_to_lcd(ELSfm)
                play_radio(0, 5)
            elif((image_index > 5) and (image_index <= 6)):
                write_to_lcd(Es)
                play_radio(0, 6)
            elif((image_index > 6) and (image_index <= 7)):
                write_to_lcd(Rm)
                play_radio(0, 7)
            elif((image_index > 7) and (image_index <= 8)):
                write_to_lcd(RebelR)
                play_radio(0, 8)
            elif((image_index > 8) and (image_index <= 9)):
                write_to_lcd(RockR)
                play_radio(0, 9)
            elif((image_index > 9) and (image_index <= 10)):
                write_to_lcd(Soulwax)
                play_radio(0, 10)
            elif((image_index > 10) and (image_index <= 11)):
                write_to_lcd(Space)
                play_radio(0, 11)
            elif((image_index > 11) and (image_index <= 12)):
                write_to_lcd(Lowlay)
                play_radio(0, 12)
            elif((image_index > 12) and (image_index <= 13)):
                write_to_lcd(Vn)
                play_radio(0, 13)
            elif((image_index > 13) and (image_index <= 14)):
                write_to_lcd(WTCr)
                play_radio(0, 14)
            elif((image_index > 14) and (image_index <= 15)):
                write_to_lcd(WSc)
                play_radio(0, 15)
            elif((image_index > 15) and (image_index <= 16)):
                write_to_lcd(WWfm)
                play_radio(0, 16)
            elif((image_index > 16) and (image_index <= 17)):
                write_to_lcd(Flfm)
                play_radio(0, 17)
            elif((image_index > 17) and (image_index <= 18)):
                write_to_lcd(LosUfm)     
                play_radio(0, 18)
            elif((image_index > 18) and (image_index <= 19)):
                write_to_lcd(BlondeB)     
                play_radio(0, 19)
            elif((image_index > 19) and (image_index <= 20)):
                write_to_lcd(LapB)     
                play_radio(0, 20)         
            
            print(f"Current Image Index: {image_index}")
        
    clkLastState = current_clk

# Change the event detect to BOTH edges for smoother tracking
GPIO.remove_event_detect(CLK)
GPIO.add_event_detect(CLK, GPIO.BOTH, callback=ausgabeFunktion, bouncetime=5)



def main():
    print("Started Radio. Abbruch mit Strg+C")
    write_to_lcd(Loading_S)
    print("Initialization of Random Start Durations")
    init_random_duration()

    try:
        # Use signal.pause() to keep the script running indefinitely
        signal.pause()
    except KeyboardInterrupt:
        print("\nCleaning up...")
    finally:
        GPIO.cleanup()



        

    

# Main Loop
if __name__ == "__main__":
    main()