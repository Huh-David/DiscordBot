# Llama Discord Bot

This Discord Bot is mainly made for our private Discord Server.

## Used Packages

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all needed packages.

```bash
pip install -r requirements.txt
```

## Required environment variables
- `BOTPASSWORD` The Discord bot token
- `Llama_Discord_Bot_SQL_Database` The database to use
- `Llama_Discord_Bot_SQL_Host` The SQL host address
- `Llama_Discord_Bot_SQL_Username` The SQL username
- `Llama_Discord_Bot_SQL_Password` The SQL password
- `PADDY_DHBW_USER` Patricks Dualis username
- `PADDY_DHBW_PASSWORD` Patricks Dualis password

The SQL stuff can be skipped if all SQL-related stuff is removed from the code.<br>
The DHBW stuff contains Patricks Dualis credentials which you hopefully don't have, so you can either disable
the DualisCrawler.py module or enter your own dualis credentials here.

## Usage

All commands have to be initiated with '!'
```python
!hello -> says 'hello'
!play url -> plays music from YouTube
!queue url -> adds music to queue
!skip -> skip song
!remove -> remove song from queue
!view -> view queue
!pause -> pause song
!resume -> resume song
!stop -> stop playback
!info [optional: username] -> get user information of yourself / someone else
!credits -> credits to us
!ping -> get bot ping
...
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
