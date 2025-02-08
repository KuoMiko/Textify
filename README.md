# Textify

This repository contains an API based application that has python as a backend code and HTML as the front-end code. The application allows user to classify environmental sounds and transcribe speech into text

by Baby Blink A. Biongcog, Robin Alexandra B. Remollo, Tristan Alejandro F. Bariñan


![demo](https://github.com/user-attachments/assets/1802ffb5-2fc1-4321-941a-33e506427c40)


## 1. Download the Dependencies

Download all the repositories by running the code below

```bash
cd /d LOCATION OF THE REQUIREMENTS HERE
pip3 install -r requirements.txt
```
You can also choose to manually download the dependencies one by one

Install the ngrok. This is necessary to make your server accessible on your phone when connected to the same network.
  1. Open the link: https://dashboard.ngrok.com/get-started/setup/windows
  2. Log-in of Sign-up to the ngrok website
  3. Scroll down the "Setup and Installation" tab
  4. Click "Download"
  5. Find and download the ngrok zip file
  6. Extract "ngrok.exe" to the "Textify" folder

## 2. Setting up the Code

- Run "Textify.py" through cmd/vscode
- Through CMD:
  - Type in: cd /d LOCATION OF THE CODE HERE, ie. cd /d C:\Users\User\OneDrive\Desktop\Texify
  - Type in: python "Textify.py"

- Run "ngrok.exe" by clicking it
- Through "ngrok.exe"
  - Type in: ngrok http 5000
  - Copy the link from the "Forwarding" tab
 
- Open the "templates" folder
- Open "index.html" with vscode
- EDIT the code: 
  - const socket = io.connect('PASTE LINK FROM NGROK HERE');, ie, const socket = io.connect('https://abcd.efg.hij.klmn.opq.rst.uvw.xyz.ngrok-free.app');
 
## 3. Open the Application
  Open the link from ngrok.

  Remember: This will only work if your device is connected to the same wifi network.

```bash
flask
flask_socketio
pyaudio
time
threading
queue
tensorflow
numpy
csv
matplotlib
IPython
scipy.io
keras_yamnet
flask_cors
ngrok
os
```
