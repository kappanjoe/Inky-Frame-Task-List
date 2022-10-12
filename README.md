# Task List for [Inky Frame](https://shop.pimoroni.com/products/inky-frame-5-7)
Task List is a user-made (i.e., very unofficial) setup for Inky Frame which syncs your Today list from Things 3 on Mac to the Inky Frame through the internet. It can also be configured to use a local server or even potentially ad-hoc but I'll leave that to you, dear user. ;) Most of the code was written in Python. The setup currently also uses Shortcuts to simplify the Mac side of things.

## Necessary Tools

1. [Inky Frame 5.7"](https://shop.pimoroni.com/products/inky-frame-5-7)
2. [Thonny]() - For uploading files to Inky Frame
3. Cloud or Local Hosting
	- The included files and instructions below will use the free tier of [Fly.io](https://fly.io/), but any simple API endpoint will do to enable updating tasks asynchronously.
4. A Mac with macOS 12.0 Monterey or later (Tested on 12.6)
5. [Things 3](https://culturedcode.com/things/) for Mac

## How to Install

### 1. Get your API endpoint up and running (Fly.io Instructions)
- Follow along with the [official Get Started documentation](https://fly.io/docs/hands-on/)
  1. **Install flyctl**
  2. **Sign up or Sign in**
  3. **Deploy Python App** (This part differs from the documentation; most notably, we won't use Docker.)
     1. Make a copy of [`secrets_template.py`](/secrets_template.py) named `secrets.py` and save it in [`task-host`](/task-host), replacing `"YOUR API KEY"` with a secret API key of your choosing (keep the quotation marks). (You can ignore the URL method until we install on Inky Frame.)
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
     5. Run the `flyctl launch` command to create your unique `fly.toml` file, linking the app to your Fly.io account
        - **App Name**: I left mine default, but you can pick anything unique
        - **Organization**: Personal
        - **Region**: Pick the closest one for you
        - **Postgresql**: No
     6. The Procfile should still be intact within [`task-host`](/task-host), but if not, create a text file named `Procfile` (no extension) containing the single line:
        ```
        web: uvicorn main:app --host 0.0.0.0 --port $PORT
        ```
     7. Run the command `flyctl deploy` and watch the magic happen
  4. **Check App Status** (You can return to the documentation again.)
     - **Take note of the hostname**; this is the domain for the URL you will use for your API endpoints.	
  5. **Visit App**
     - If you visit the base level domain directly, your browser should display a single line of text; "Nothing to see here."

### 2. Install the Shortcut
- Double click the shortcut file and the Shortcuts app on your Mac will begin import.
- Input your API URL and add the API Key to the headers as prompted. The correct URL is the new hostname created for your Fly.io app, appending `/tasks` to the end (it should look something like `https://app-name.fly.dev/tasks`).
- You may need to grant permissions to use scripts/AppleScript the first time you run the shortcut. "Always Allow" to avoid the prompt every single time the shortcut runs.

### 3. ~~Install the Automator App~~
- ~~Drag the application to the "Applications" folder on your Mac. Open the app. (You may need to hold down `option` while opening to grant permission as the code is not signed.)~~
- **The app is [broken](https://github.com/kappanjoe/Inky-Frame-Task-List/issues/1) and has been removed.** I will update the repository once I've found another solution, but for now, you will need to run the shortcut manually when you want to send updates to the API endpoint.

### 4. Edit `WIFI_CONFIG.py` and `secrets.py`
- Similar to what we did with the Fly.io deployment, make a copy of [`secrets_template.py`](/secrets_template.py) named `secrets.py`, **as well as** [`WIFI_CONFIG_template.py`](/secrets_template.py) (named `WIFI_CONFIG.py`), saving both in [`pico-image`](/pico-image).
- In the new `secrets.py`, replace `"YOUR API KEY"` with the same secret API key as before. Replace `"YOUR API URL"` with the same URL as you used to import the shortcut.
- Replace the SSID and PSK values in `WIFI_CONFIG.py` with the network name and password you want your Inky Frame to use to connect wirelessly.
- Replace the COUNTRY value with the two-letter country code for your country [(look it up here)](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). This is required to ensure Inky Frame uses the correct networking protocols which can differ country to country... or something like that.
- Don't forget to keep quotation marks surrounding each of the edited values! They need to be read as strings.

### 5. Install Thonny
```
pip3 install thonny
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

### v0.5

- Remove Automator app
- Add README.md
- Add fly.toml to .gitignore (should be private - oops)
- Add tinyweb to .gitignore (unused)

### v0.0

- Initial commit
