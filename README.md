# Task List for [Inky Frame](https://shop.pimoroni.com/products/inky-frame-5-7)
Task List is a user-made (i.e., very unofficial) setup for Inky Frame which syncs your Today list from Things 3 on Mac to the Inky Frame through the internet. Adept users should be able to easliy customize it to run adhoc or on a local server. On the Mac side, a Launch Agent runs a Shortcut  on a 30 min. interval to grab the task list from Things 3 and upload the data to an API Endpoint (with authorization). On the Inky Frame side, the unit calls the same API endpoint (with auth.) on a 30 min. interval to download the most recent version of the tasks.

## Necessary Tools

1. [Inky Frame 5.7"](https://shop.pimoroni.com/products/inky-frame-5-7)
2. [Thonny]() - For uploading files to Inky Frame
3. Cloud or Local Hosting
	- The included files and instructions below will use the free tier of [Fly.io](https://fly.io/), but any simple API endpoint will do to enable updating tasks asynchronously.
4. A Mac with macOS 12.0 Monterey or later (Tested on 12.6)
5. [Things 3](https://culturedcode.com/things/) for Mac

## How to Install

### 1. Get your API up and running (Fly.io Instructions)
- Follow along with the [official Get Started documentation](https://fly.io/docs/hands-on/)
  1. **Install flyctl**
  2. **Sign up or Sign in**
  3. **Deploy API** (This part differs from the standard documentation; most notably, we won't use Docker.)
     1. Set up your files:
        1. Make a copy of [`secrets_template.py`](/secrets_template.py) named `secrets.py` and save it in [`task-host`](/task-host).
        2. Replace `"YOUR API KEY"` in `secrets.py` with a secret API key of your choosing (keep the quotation marks).
        - **IMPORTANT**: Authorization has been removed for getting tasks in image form. API Key is required only for posting new tasks and getting tasks in JSON format. [Click here](https://github.com/kappanjoe/Inky-Frame-Task-List/tree/a089553df54437dbd3523132bd8fce13a7e81834) for text-based version with key-protected endpoints.
        3. Save a font file of your choice within `task-host`. (TrueType, OpenType, and other file types readable by the [FreeType library](https://freetype.org) are supported.)
        4. In [`task-host/main.py`](/task-host/main.py), replace `"SF-Pro-Text-Medium.otf"` with the filename of the font you included.
     2. Next, we need to set up a python virtual environment:
        1. In the [`task-host`](/task-host) folder, create the virtual environment by running:
           ```
           % python3 -m venv venv
           ```
        2. Activate venv by running:
           ```
           % . venv/bin/activate
           ```
     3. While inside the virtual environment, install the dependencies by running:
        ```
        python3 -m pip install -r requirements.txt
        ```
        - Installs:
          - **FastAPI** - Creates API endpoints for storing tasks
          - **uvicorn** - Connects the Python app to the outside world
          - **pydantic** - Creates base models of the object classes used for parsing tasks from Things 3
     4. Deactivate the venv by running:
        ```
        deactivate
        ```
     5. Run the `% flyctl launch` command to create your unique `fly.toml` file, linking the app to your Fly.io account
        - **App Name**: I left mine default, but you can pick anything unique
        - **Organization**: Personal
        - **Region**: Pick the closest one for you
        - **Postgresql**: No
     6. The Procfile should still be intact within [`task-host`](/task-host), but if not, create a text file named `Procfile` (no extension) containing the single line:
        ```
        web: uvicorn main:app --host 0.0.0.0 --port $PORT
        ```
     7. Run the command `% flyctl deploy` and watch the magic happen
  4. **Check API Status** (You can return to the documentation again.)
     - **Take note of the hostname**; this is the domain for the URL you will use for your API endpoints.	
  5. **Visit API**
     - If you visit the base level domain directly, your browser should display a single line of text; "Nothing to see here."

### 2. Install the Shortcut
- Double click the shortcut file and the Shortcuts app on your Mac will begin import.
- Input your API URL and add the API Key to the headers as prompted. The correct URL is the new hostname created for your Fly.io app, appending `/tasks` to the end (it should look something like `https://app-name.fly.dev/tasks`).
- You may need to grant permissions to use scripts/AppleScript the first time you run the shortcut. "Always Allow" to avoid the prompt every single time the shortcut runs.

### 3. Install the Launch Agent
- Save the .plist `com.kappanjoe.tasklist.uploadagent` to your user Library in the directory `~/Library/LaunchAgents`, then logout. After login, the Launch Agent will run the previously installed shortcut every 1800 seconds (30 min.) or so. If you change the shortcut name to anything other than "Upload Task List to Cloud", make sure you edit the corresponding string inside the .plist to match.

### 4. Edit `WIFI_CONFIG.py` & ENDPOINT URL
- Make a copy of [`WIFI_CONFIG_template.py`](/WIFI_CONFIG_template.py) named `WIFI_CONFIG.py` and save it in [`pico-image`](/pico-image).
- Replace the SSID and PSK values in `WIFI_CONFIG.py` with the network name and password you want your Inky Frame to use to connect wirelessly.
- Replace the COUNTRY value with the two-letter country code for your country [(look it up here)](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). This is required to ensure Inky Frame uses the correct networking protocols which can differ country to country... or something like that.
- Don't forget to keep quotation marks!
- Replace "YOURHOSTNAME" in [`pico-image/main.py`](/pico-image/main.py) with the host name of the new API you set up in Step 1.

### 5. Install Thonny
```
% pip3 install thonny
```

### 6. Connect to Inky Frame
- I recommend skimming over Pimoroni's [Getting Started with Inky Frame](https://learn.pimoroni.com/article/getting-started-with-inky-frame) doc if you aren't already familiar with using your Inky Frame.

### 7. Use Thonny to upload all the files within [`pico-image`](/pico-image) to Inky Frame
- The root of Inky Frame should now match the inside of `pico-image`.

### 8. Unplug Inky Frame and turn on the battery!
- When `main.py` runs, Inky Frame will download the latest version of your tasks from your API endpoint, and go to sleep for roughly 30 minutes before looping over the process again.
- Each time you turn on the battery, you will need to wake Inky Frame up once by pressing a button on the front (the activity light will turn on when awake). After the script runs once, it will then automatically sleep and wake every 30 minutes until the battery is turned off.
- The cycle time can be adjusted up to 255 minutes by editing the value of `UPDATE_INTERVAL` in [`pico-image/main.py`](pico-image/main.py).

## Changelog

### v0.9

- Adjusted colors to reduce dithering from 3-bit palette rendering
- [3-bit palette color reference](https://github.com/pimoroni/pimoroni-pico/blob/6ebf1a97f870ba49f1ea5b4505a6238757d8eb05/libraries/pico_graphics/pico_graphics.hpp#L308-L315)

### v0.8

- Styling changes to images generated by task-host

### v0.7

- Convert API to image-based flow
- Clean up source code

### v0.6

- Add Launch Agent to run shortcut on an interval

### v0.5

- Remove Automator app
- Add README.md
- Add fly.toml to .gitignore (should be private - oops)
- Add tinyweb to .gitignore (unused)

### v0.0

- Initial commit
