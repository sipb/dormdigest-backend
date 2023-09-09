# Developer Onboarding

Relevant permission bits

- Get added to `sipb-dormdigest-admin` Moira mailing list to manage Scripts locker, SQL database, and XVM for dormdigest
  - Scripts locker can be found at `/mit/dormdigest` or `/afs/sipb/project/dormdigest`
  - To manage the mail_scripts or web_scripts, you will need to do `ssh dormdigest@scripts.mit.edu` from AFS
  - To manage the SQL database, go to: <https://scripts.mit.edu/mysql/>
- Get added to this repo as a collaborator to push changes
  - For development fork this repo to your profile. Commit changes, and then make a pull request to synchronize your fork with the main (or relevant) branch
- Get the `creds.py` file from a current maintainer / project member and put it in the configs/ folder.
  - This file has the credentials for the MySQL database running on Scripts SQL service
  - You should look over it and select the corresponding mode (either `prod` for production db or `test` for test db)
- Get the official certificates for the web service and also put them in the configs/ folder

## Development Best Practices

* **Python Virtual Environment** 
  * When working in your local code environment, it's recommended to work off a virtual environment (to ensure there's no compatibility issues with the SQLalchemy + dependencies versions). 
  * To do so, on your first time run:
    * **NOTE:** If running on XVM server, it's very likely that the default Python3 version is v3.6, whereas this project depends on v3.10. As a result, you will need to change references to `python3` to `python3.10` and `pip3` to `python3.10 -m pip`
    * `sudo apt install libmysqlclient-dev` (Installs MySQL client)
    * `sudo apt-get install python3-dev` (or `python3.10-dev`, since that's the Python version we're currently using)
    * `python3 -m venv env` (Creates a local environment in current folder)
    * `source env/bin/activate` (Activates virtual environment)
    * `pip3 install -r requirements.txt` (Install necessary packages)
  * When you exit your workspace, remember to run: 
    * `deactivate`
  * Then, in the future, when you come back, simply do:
    * `source env/bin/activate`
    * **Note:** If you are using Visual Studio for your code editor, normally it will automatically load in your virtual environment (if found in current working directory) when you run your code. This saves time from having to load and unload your venv each time.
* Pulling emails from mail scripts
  * In the initial stages, we're saving all emails that errored out at `mail_scripts/saved` on the dormdigest locker. To retrieve it, first log into Athena and cd into a local directory (one owned by you) folder. Then do:
    * `rsync -av /mit/dormdigest/mail_scripts/saved/ ./saved/`
  * To copy it back to your computer, do something like:
    * `scp -r kerb@athena.dialup.mit.edu:~/dormdigest/mail_scripts/saved/ ./test_emails/`
* Pushing frontend build to XVM
  * Because XVM doesn't support node 18 properly, whenever you want to run a new build in production, you will need to build it locally with `npm run build` and then secure copy the build files onto the server. An example command is:
  * `scp -r ~/Documents/SIPB/dormdigest-frontend/build/* root@dormdigest.xvm.mit.edu:/home/dorm/dormdigest-frontend/build/`
* (NOT BEING USED) Setup Postgres database
  * `sudo apt install postgresql postgresql-contrib`
  * `sudo -u postgres psql`
  * `CREATE DATABASE dormdigest_prod;`
* To run the frontend static files server, do:
  * `http-server -S -C /etc/letsencrypt/live/dormdigest.xvm.mit.edu/fullchain.pem -K /etc/letsencrypt/live/dormdigest.xvm.mit.edu/privkey.pem -p 443 ./build -- & > server_log.txt`

## Optimizations

* Setting up **Redis**
  * To improve the performance of our FastAPI server, we added support for function caching via redis
  * First, to install Redis:
    * `curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg`
    * `echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list`
    * `sudo apt-get update`
    * `sudo apt-get install redis`
    * `sudo apt install redis-server`
  * Verify it's working with:
    * `systemctl status redis`
    * `redis-cli ping` (should get back PONG)
    * Run `test_redis.py`. You should see both operations taking about 5 seconds each the first time running the script, and then almost instant the second time.
