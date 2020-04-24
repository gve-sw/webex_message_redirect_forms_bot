# Webex Teams redirection Bot with cards and buttons

This sample code demonstrates how to take a simple input from a user and send it to a teams space. 
This can best used to support requiremts without direct contact with the IT team

## Contacts
* Max Acquatella (macquate@cisco.com)
* Gerardo Chaves (gchaves@cisco.com)

## Requirements

Python 3.6 or later
A publicly accessible address and certificate or use of tunneling techniques such as **ngrok**

These instructions are written assuming the use of Linux or MacOS for commands to start the script, but it should run on Windows as well. Just look for equivalent ways to install/run ngrok and start python scripts and issue git commands. 


## Installation
In order to run this in your environment, you can start by cloning the repo and 
setting your shell environment to that folder:
```
$ git clone https://wwwin-github.cisco.com/gve/webex_message_redirect_forms_bot.git
cd webex_message_redirect_forms_bot

```

Next, if you don't already have a Cisco Webex account, go ahead and register for one.  They are free.

### Webex Teams Bot

This sample scripts requires de use of a Webex Teams Bot. If you do not have one already which you plan on using, follow these instructions to create a new one:

Go to [https://developer.ciscospark.com/add-app.html](https://developer.ciscospark.com/add-app.html). You can also navigate to this location from the the main page at developer.webex.com, log in and click on your avatar on the upper right of the screen and select "My Webex Apps" from the pop-up menu. 

1. Click create bot
2. Fill out all the details about your bot.
3. Click "Add Bot" and make sure to copy your **Bot's Access Token** which you will need to specify as WEBEX_TEAMS_ACCESS_TOKEN python variable as seen below (this token is shown only once, if you come back to look for it after closing the page it will not be shown so, if you did not save it, you will have to generate a new one). Also take note of the **Bot Username** that was generated, you will need this to add the bot to the space that receives the requests/messages from users. 

### Webex Teams space to receive notifications
This sample script uses a Webex Teams Space (referred to as Room in the API documentation) to re-direct requests it receives as messages from individual users. 
You can use an existing space for which you would need to obtain the Space or ID. You can list all rooms/spaces that your are a member of by using this API call from the Webex Teams documentation: https://developer.webex.com/docs/api/v1/rooms/list-rooms
You can also create a new Space (room) in Webex Teams and extract the Room Id from the new Space from this link: https://developer.webex.com/docs/api/v1/rooms/list-rooms

That space(room) ID will be stored in the DESTINATION_SPACE_ID as specified below. 

IMPORTANT: You must add the Bot you created in the steps above to this space (using its **Bot Username**). You also want to add any other Webex Teams users that you would like to see the messages/notifications from the users to this space. This is easiest done manually... from the user that was used to create the space (most likely your personal webex teams account) just open the new space on a webex teams client and go to "add participants" to search for the Bot Username and add it. 

### Python environement setup
If you wish to use python environments to run this script, open a terminal console window and navigate to the folder containing the cloned repo. Create a virtualenv and install the module.

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
You can also just run it using the existing environment on your computer, just make sure the libraries specified in requirements.txt are installed. 


### Configuration variables

The following variables are needed for the sample to run. The WEBHOOK_URL will be discussed further below:

* WEBEX_TEAMS_ACCESS_TOKEN -- Access token for a Webex bot
* WEBHOOK_URL -- URL for Webex Webhooks (ie: https://2fXX9c.ngrok.io)
* PORT - Port for Webhook URL (ie: the port param passed to ngrok)
* DESTINATION_SPACE_ID --- The space that receives the user's messages as discussed above

The repository already has a configuration file ready to edit where you can
add the values needed. It is in **config_default.py**

Just rename the **config_default.py** to **config.py** and enter your information there before running the code.

## External webhook

This sample script must expose a public IP address in order to receive notifications
about Webex events.  

For testing, **ngrok** (https://ngrok.com/) can be used to tunnel traffic
back to your server if your machine sits behind a firewall.
**ngrok** will make easy for you to develop your code with a live bot.
You can find installation instructions here: https://ngrok.com/download

## Running the script

This sample script leverages the Flask web service micro-framework
(see http://flask.pocoo.org/).  By default the web server will be reachable at
port 5000 you can change this default if desired (see `flask_app.run(...)`).
In our app we read the port from the PORT environment variable.

Upon startup this app create webhooks so that our bot is notified when users
send it messages or interact with any cards that have been posted.   In
response to any messages it will post a simple form filling card.  In response
to a user submitting a form, the details of that response will be posted in
the space.

### Starting ngrok 

If you are testing the script and will use **ngrok** because you do not yet have a way to run the Flask web server with an external address and a valid certificate (Webex Teams Webhooks require HTTPS protocol), then open a separate terminal window and start the service:

`ngrok http 5000`

You should see a screen that looks like this:

```
ngrok by @inconshreveable                                                                                                                                 (Ctrl+C to quit)

Session Status                online
Version                       2.2.4
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://this.is.the.url.you.need -> localhost:5000
Forwarding                    https://this.is.the.url.you.need -> localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              2       0       0.00    0.00    0.77    1.16

HTTP Requests
-------------

POST /                         200 OK
```

### Starting the main script

To start the main python script that launches the Flask application that implements the bot, just run the **support_redirection_bot.py** script from a separate terminal window (the one running ngrok will be blocked running that utility):

```python support_redirection_bot.py```

It should report that the Flask application is running and listening to port 5000

### Testing
After you add the bot to the "Destination" space that has the users that want to receive the messages, send a direct message to the Bot using the **Bot Username**. The content of the message is irrelevant, but it will trigger the bot respond with a form for you fill out and enter a message to send to the "Destination" space. Once you fill out the message and submit, the bot will forward that message alongside the senders name and email address to the "Destination" space. 


