import requests
import xml.etree.ElementTree as ET
import readGoogleSheets
import random
import subprocess
import time
#channels = ['UCuDm45jKrsTeEpx7BayVaiw','UCJFP-5V2-0BFeVmKifG0H_Q' , 'UC6jNDNkoOKQfB5djK2IBDoA']
channels = readGoogleSheets.main()
for channelid in channels:
    urlvideo = "https://www.youtube.com/feeds/videos.xml?channel_id="+channelid

    # Send a request with a User-Agent header
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    r = requests.get(urlvideo, headers=headers)

    # Check if the request was successful
    if r.status_code != 200:
        print(f"Failed to retrieve data." + channelid + " Status Code: {r.status_code}")
        exit()

    data = r.content

    try:
        root = ET.fromstring(data.decode())
    except ET.ParseError as e:
        print(f"XML Parsing Error: {e}")
        exit()

    # Define the namespace used in the YouTube XML feed
    namespace = {'yt': 'http://www.youtube.com/xml/schemas/2015'}

    # Find all entries in the XML feed
    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
    random.shuffle(entries)
    for entry in entries:
        title = entry.find('.//{http://www.w3.org/2005/Atom}title')
        duration = entry.find('.//yt:duration', namespaces=namespace)

        # Check if the video has a duration element and the duration is longer than a threshold (e.g., 300 seconds)
        #if title is not None and duration is not None and int(duration.attrib['seconds']) > 90:
        print('Title:', title.text)

        views = entry.find('.//yt:statistics', namespaces=namespace)
        if views is not None and 'viewCount' in views.attrib:
            print('Views:', views.attrib['viewCount'])

        video_url = entry.find('.//{http://www.w3.org/2005/Atom}link[@rel="alternate"]', namespaces=namespace)
        if video_url is not None and 'href' in video_url.attrib:
            url = video_url.attrib['href']
            print('Video URL:', url)
            #cmd = "python3 C:\\Users\\user\\Documents\\automatizacionDONPODCAST\\input_youtube_link_1min.py "+url+" Transcribir C:\\Users\\user\\Documents\\automatizacionDONPODCAST\\touploadMP4\\"
            #cmd = "python3 input_youtube_link_cmd.py "+url+" Transcribir touploadMP4/"
            #cmd = cmd.replace("\\", "\\\\").replace("C:\\\\", "C\\:\\\\")
            # Ejecutar el comando ls y capturar la salida
            resultado = subprocess.run(["ls"], capture_output=True, text=True)
            # Imprimir la salida
            print("Salida del comando ls:")
            #time.sleep(5)
            subprocess.run(cmd, check=True)
            print(resultado.stdout)
            exit()

        likes = entry.find('.//yt:likes', namespaces=namespace)
        if likes is not None and 'count' in likes.attrib:
            print('Likes:', likes.attrib['count'])

        print('-' * 30)
        break;
