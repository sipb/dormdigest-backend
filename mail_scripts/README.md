# mail_scripts/

The project locker listens for and passes along emails, yet due to current limitations, a separate server processes the emails and hosts the database.

Enable [mail scripts](https://scripts.mit.edu/mail/) in the project locker, then configure it by syncing this directory's files into the locker's corresponding `mail_scripts` directory.

## procmail

[procmail](https://userpages.umbc.edu/~ian/procmail.html) is a mail filtering system.

The file for this project runs the mail into `send_to_backend.py`.

## send_to_backend.py

It does what it says on the tin.

But it needs a few environment variables defined:
* `DORMDIGEST_EAT_ENDPOINT`: URL of the `/eat` API endpoint.
* `DORMDIGEST_TOKEN`: Token used for authentication. Emails sent to the endpoint will not be processed unless they have a valid authentication token.
* `DORMDIGEST_WEBHOOK`: Mattermost webhook URL to post debug messages to.

(these may be replaced with a config file)