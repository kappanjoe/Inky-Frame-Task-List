# Task List for [Inky Frame](https://shop.pimoroni.com/products/inky-frame-5-7)
Task List is a user-made (i.e., very unofficial) setup for Inky Frame which syncs your Today list from Things 3 on Mac to the Inky Frame in the cloud. Most of the code was written in Python. The setup currently also uses Shortcuts and Automator technologies to simplify the Mac side of the setup.

## Necessary Tools

1. [Inky Frame 5.7"](https://shop.pimoroni.com/products/inky-frame-5-7)
2. [Thonny]() - For uploading files to Inky Frame
3. Cloud or Local Hosting
	- The included files and instructions below will use the free tier of [Fly.io](https://fly.io/), but any simple API endpoint will do to enable updating tasks asynchronously.
4. A Mac with macOS 12.0 Monterey or later (Tested on 12.6)
5. Things 3 for Mac

## How to Install

### 1. Get your endpoint up and running (Fly.io Instructions)
	- Follow along with the [official Get Started documentation](https://fly.io/docs/hands-on/)
	a. Install flyctl
	b. Sign up or Sign in
	c. Deploy Python App (This part differs from the documentation; most notably, we won't use Docker.)
		- Make a copy of [`secrets_template.py`](/secrets_template.py) named `secrets.py` and save it in [`task-host`](/task-host), replacing `"YOUR API KEY"` with a secret API key of your choosing (keep the quotation marks). (You can ignore the URL method until we install on Inky Frame.)
		- Next, we need to set up a python virtual environment:
			i. In the [`task-host`](/task-host) folder, run `python3 -m venv venv` to create the virtual environment
			ii. Activate venv using `. venv/bin/activate`
		- While inside the virtual environment, install the dependencies using `python3 -m pip install -r requirements.txt`. Installs:
			- FastAPI - Creates API endpoints for storing tasks
			- uvicorn - Connects the Python app to the outside world
			- pydantic - Creates base models of the object classes used for parsing tasks from Things 3
		- Deactivate the venv by entering `deactivate`
		- Run the `flyctl launch` command to create your unique `fly.toml` file, linking the app to your Fly.io account
			- App Name: I left mine default, but you can pick anything unique
			- Organization: Personal
			- Region: Pick the closest one for you
			- Postgresql: No
		- The Procfile should still be intact within [`task-host`](/task-host), but if not, create a text file named `Procfile` (no extension) with the single line:
			`web: uvicorn main:app --host 0.0.0.0 --port $PORT`
		- Run the command `flyctl deploy` and watch the magic happen
	d. Check App Status (You can return to the documentation again.)
		- **Take note of the hostname**; this is the domain for the URL you will use for your API endpoints.
	e. Visit App
		- If you visit the base level domain directly, your browser should display a single line of text; "Nothing to see here."

### 2. Install the Shortcut
	- Double click the Shortcuts file and the Shortcuts app on your Mac will begin the install process. Input your API URL and add the API Key to the headers when prompted. The correct URL is the new hostname created for your Fly.io app, appending `/tasks` to the end (it should look something like `https://app-name.fly.dev/tasks`). You may need to grant permissions to use scripts/AppleScript the first time you run the shortcut. Grant "Always Allow" to avoid the prompt every single time the shortcut runs.

### 3. ~~Install the Automator App
	- Drag the application to the "Applications" folder on your Mac. Open the app. (You may need to hold down `option` while opening to grant permission as the code is not signed.)~~
	- **The app is [broken](https://github.com/kappanjoe/Inky-Frame-Task-List/issues/1) and has been removed.** I will update the repository once I've found another solution, but for now, you will need to run the shortcut manually when you want to send updates to the API endpoint.

### 4. Edit `WIFI_CONFIG.py` and `secrets.py`
	- Similar to what we did with the Fly.io deployment, make a copy of [`secrets_template.py`](/secrets_template.py) named `secrets.py`, **as well as** [`WIFI_CONFIG_template.py`](/secrets_template.py) (named `WIFI_CONFIG.py`), saving both in [`pico-image`](/pico-image).
	- In the new `secrets.py`, replacing `"YOUR API KEY"` with the same secret API key as before. Replace `"YOUR API KEY"` with the new hostname created for your Fly.io app, appending `/tasks` to the end. The URL should look something like `https://app-name.fly.dev/tasks`.
	- Replace the SSID and PSK values in `WIFI_CONFIG.py` with the network name and password you want your Inky Frame to connect to wirelessly.
	- Replace the COUNTRY value with the two-letter country code for your country [(look it up here)](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). This is required to ensure Inky Frame uses the correct networking protocols which can differ country to country... or something like that.
	- Don't forget to keep the quotation marks surrounding each of the edited values!
	- The API key is technically optional, but I've included it to keep your tasks away from prying eyes.

### 5. Install Thonny
	```
	pip3 install thonny
	```

### 6. Connect to Inky Frame
	- I recommend skimming over Pimoroni's [Getting Started with Inky Frame](https://learn.pimoroni.com/article/getting-started-with-inky-frame) doc if you aren't already familiar with working with using RasPi/Inky Frame

### 7. Use Thonny to upload all the files within [`pico-image`](/pico-image) to Inky Frame

### 8. Unplug Inky Frame and turn on the battery!
	- Inky Frame will download the latest version of your tasks from your API endpoint, and go to sleep for 30 minutes before looping over the process again. You may need to press a button on the front of the unit to wake it up the first time. The activity and wireless lights will turn on while Inky Frame is working.

## Changelog

### v0.5

- Remove Automator app
- Add README.md
- Add fly.toml to .gitignore (should be private - oops)
- Add tinyweb to .gitignore (unused)

### v0.0

- Initial commit
