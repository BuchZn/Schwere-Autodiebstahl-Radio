# precompile_images.py — einmalig ausführen
import os
from PIL import Image
import struct

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


images = {
    'blc':     './img/BLC.jpeg',
    'nonstop': './img/NonStopPop.jpg',
    'blueark': './img/BlueArk.jpeg',
    'channelx': './img/ChannelX.jpeg',
    'eastlostfm': './img/EastLostFm.jpeg',
    'eastlosantos': './img/EastLosantos.jpeg',
    'radiomirrow': './img/RadioMirrow.jpeg',
    'rebelradio': './img/RebelRadio.jpeg',
    'rockradio': './img/RockRadio.jpeg',
    'soulwaxfm': './img/SoulwaxFM.jpeg',
    'spacefm': './img/SpaceFM.jpeg',
    'thelowlay': './img/Thelowlay.jpeg',
    'vineyard': './img/Vineyard.jpeg',
    'wctr': './img/WCTR.jpeg',
    'westcoastclassic': './img/WCclassics.jpeg',
    'worldwidefm': './img/WorldWideFM.jpg',
    'flylofm': './img/FlyloFM.jpeg',
    'losu': './img/LosSantosU.jpg',
    'lap': './img/LapR.jpg',
    'blonde': './img/Blonded_Radio.jpeg',
    'loading': './img/Loading_Screen.jpg',
}

for name, path in images.items():
    buf = create_buffer(path)
    with open(f'./img/{name}.bin', 'wb') as f:
        f.write(buf)
    print(f"Gespeichert: {name}.bin")