# MFC Stat Tracker

Depends upon the MFC API located [here](https://gitlab.cloud-technology.io/MFC/MFC-ELO).
You'll need to setup the API accordingly otherwise only logging events will work properly.

## Quick Start

Ensure you have a copy of the MFC API

Clone the repository and then do the following

1. Create a `.env` in the root (the directory above `tracker/`)
2. Within the `.env` you'll need to define a few variables:
    - `RCON_IP`
      - The IP to your server
    - `RCON_PORT`
        - The port at which your server is hosting RCON
    - `RCON_PASSWORD`
        - The password set for RCOn
    - `API_URL`
        - The URL of your API
    - `API_TOKEN`
        - The authorization token granted by the API
    - `MATCH_ADMINS`
        - The Mordhau users who may invoke commands. 
          It is a comma delimited list of playfab ids
            - E.g. `MATCH_ADMINS=5E92E0B55E90869C,KE92E0B55E90869D,`
    - `MATCH_VALID_MAPS`
        - The valid maps that can used in a game, 
          it is a comma delimited list of maps
            - E.g. `MATCH_VALID_MAPS=skm_moshpit,skm_contraband,...`

3. Create your virtual environment:
   
    For Mac/Linux:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4. Run the program:
   ```bash
   python -m tracker
   ```

## In Game Usage

Type `match help` for a list of match commands, otherwise the `register` command can be used to register the invoker
with the API.

## Configuration
All config values are passed via environment variables. See [Environment Variables](#Environment Variables)

Generally it is best practice to create a `.env` file in the root directory and set your variables there.

## Logging

For logging to work you *must* define a `log_config.yaml` file within the `tracker` directory based on the the python
logging [dictConfig](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details) *or* set the 
appropriate log path in your environment, see **Environment Variables**. 

Within your own `log_config.yaml`, assuming you don't use the default, ensure you set `disable_existing_loggers` to
**false**, otherwise some log messages may not be captured from external libraries.

An example config in yaml, and the one that ships by default:

```yaml
version: 1
disable_existing_loggers: false # Important, otherwise some lib logs may be dropped
formatters:
    standard:
        format: '[%(asctime)s][%(threadName)s][%(name)s.%(funcName)s:%(lineno)d][%(levelname)s] %(message)s'
    raw_rcon:
        format: '%(message)s'
handlers:
    default_stream_handler:
        class: logging.StreamHandler
        formatter: standard
        level: INFO
        stream: ext://sys.stdout
    default_file_handler:
        backupCount: 5
        class: logging.handlers.RotatingFileHandler
        filename: rcon.log
        formatter: standard
        level: DEBUG
    raw_rcon_file_handler:
        backupCount: 5
        class: logging.handlers.RotatingFileHandler
        filename: raw_rcon.log
        formatter: raw_rcon
        level: DEBUG
    error_file_handler:
        backupCount: 5
        class: logging.handlers.RotatingFileHandler
        delay: true
        filename: rcon_error.log
        formatter: standard
        level: ERROR
loggers:
    '': # The root logger, best to leave it undefined (don't enter a string)
        handlers:
            - default_stream_handler
            - default_file_handler
            - error_file_handler
        level: DEBUG
        propagate: false
    'raw_rcon': # Defined to capture RCON logs
        handlers:
            - raw_rcon_file_handler
        level: DEBUG
        propagate: false
```

## Environment Variables

It is highly encouraged that a `.env` file is defined in the root directory with your variables. If you do not do this,
you will need to export all of your variables into your local environment *before* running the tracker.

### RCON

All RCON variables are preceded by `RCON_`

| Variable Name   | Example Value   | Description
| :---            | :---            | :---
| RCON_IP         | 192.187.124.138 | The IP of the Mordhau server to connect RCON to
| RCON_PORT       | 54321           | The PORT where RCON is running on the Mordhau server
| RCON_PASSWORD   | somePassword    | The password needed to authenticate RCON

### API

All API variables are preceded by `API_`

| Variable Name   | Example Value         | Description
| :---            | :---                  | :---
| API_URL         | https://yourapi.api/  | The URL to your API
| API_TOKEN       | awdjw1oidj10a89WWD... | The authorization token (JWT) issued by the API for authentication


### MATCH

All MATCH variables are preceded by `MATCH_`

This defines in-game configuration values for the Mordhau RCON

| Variable Name   | Example Value               | Description
| :---            | :---                        | :---
| MATCH_ADMINS    | 5E92E0B55E90869C,BW...      | The users permitted to run commands on the tracker, this is a list of playfab IDs defining Mordhau players
| MATCH_VALID_MAPS| skm_moshpit,skm_contraband  | The maps that can be passed to the tracker via the `match setup` command


### CHAT

All CHAT variables are preceded by `CHAT_`

This defines vars related to Mordhau chat commands etc.

| Variable Name   | Example Value               | Description
| :---            | :---                        | :---
| CHAT_PREFIX     | `!`                          | The prefix used to invoke commands, defaults to `-`