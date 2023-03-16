# Developer Onboarding

Relevant permission bits

- Get added to `sipb-dormdigest-admin` Moira mailing list to manage Scripts locker, SQL database, and XVM for dormdigest
  - Scripts locker can be found at `/mit/dormdigest` or `/afs/sipb/project/dormdigest`
  - To manage the mail_scripts or web_scripts, you will need to do `ssh dormdigest@scripts.mit.edu` from AFS
  - To manage the SQL database, go to: <https://scripts.mit.edu/mysql/>
- Get added to this repo as a collaborator to push changes
  - For development fork this repo to your profile. Commit changes, and then make a pull request to synchronize your fork with the main (or relevant) branch
- Get the `creds.py` file from a current maintainer / project member and put it in the src/ folder.
  - This file has the credentials for the MySQL database running on Scripts SQL service
  - You should look over it and select the corresponding mode (either `prod` for production db or `test` for test db)

## Development Best Practices

* When working in your local code environment, it's recommended to work off a virtual environment (to ensure there's no compatibility issues with the SQLalchemy + dependencies versions). 
* To do so, on your first time run:
  * `python3 -m venv env` (Creates a local environment in current folder)
  * `source env/bin/activate` (Activates virtual environment)
  * `pip3 install -r requirements.txt` (Install necessary packages)
* When you exit your workspace, remember to run: 
  * `deactivate`
* Then, in the future, when you come back, simply do:
  * `source env/bin/activate`