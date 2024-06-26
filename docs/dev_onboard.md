# Developer Onboarding

Relevant permission bits

- Get added to `sipb-dormdigest-admin` Moira mailing list to manage Scripts locker, SQL database, and XVM for dormdigest
  - Scripts locker can be found at `/mit/dormdigest` or `/afs/sipb/project/dormdigest`
  - To manage the mail_scripts or web_scripts, you will need to do `ssh dormdigest@scripts.mit.edu` from AFS
  - To manage the SQL database, go to: <https://scripts.mit.edu/mysql/>
- Get added to this repo as a collaborator to push changes
  - For development fork this repo to your profile. Commit changes, and then make a pull request to synchronize your fork with the main (or relevant) branch
- Get the `creds.py` and `server_configs.py` file from a current maintainer / project member and put it in the `src/configs/` folder.
  - This file has the credentials for the MySQL database running on Scripts SQL service

## Development Onboarding

* **Python Virtual Environment** 
  * When working in your local code environment, it's recommended to work off a virtual environment (to ensure there's no compatibility issues with the SQLalchemy + dependencies versions). 
  * To do so, on your first time run:
    * **NOTE:** If running on XVM server, it's very likely that the default Python3 version is v3.6, whereas this project depends on v3.10. As a result, you will need to change references to `python3` to `python3.10` and `pip3` to `python3.10 -m pip`
    * `sudo apt-get install python3-dev` (or `python3.10-dev`, since that's the Python version we're currently using)
    * `python3 -m venv env` (Creates a local environment in current folder named `env`)
    * `source env/bin/activate` (Activates virtual environment)
    * `pip3 install -r requirements.txt` (Install necessary packages)
  * When you exit your workspace, remember to run: 
    * `deactivate`
  * Then, in the future, when you come back, simply do:
    * `source env/bin/activate`
    * **Note:** If you are using Visual Studio for your code editor, normally it will automatically load in your virtual environment (if found in current working directory) when you run your code. This saves time from having to load and unload your venv each time.
* (OPTIONAL) Creating your local HTTPS certificates
  * For security, we require that the FastAPI server runs with HTTPS enabled. You can create your own self-signed certificates through the `mkcert` tool.
  * On Linux/Windows:
    * Install `nss`, such as `sudo dnf install nss-tools`. `mkcert` will tell you how to install it if you skip this step.
    * Download `mkcert` from https://github.com/FiloSottile/mkcert/releases and put it in your PATH
  * On Mac:
    * `brew install mkcert`
    * `brew install nss` (if you use Firefox)
    * `mkcert -install`
    * Navigate into the dormdigest-backend folder at `src/configs/`, and then run:
      * `mkcert localhost 127.0.0.1`
      * You should now have two files named something like `localhost+1.pem` and `localhost+1-key.pem`
    * Rename the file with `key` to `key.pem` and then rename the other file `cert.pem`.
* (OPTIONAL) Setting up local **Redis server**
  * To improve the performance of our FastAPI server, we added support for function caching via redis
  * First, to install Redis:
    * On Linux:
      * `curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg`
      * `echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list`
      * `sudo apt-get update`
      * `sudo apt-get install redis`
      * `sudo systemctl enable --now redis`
      * Verify it's working with:
        * `systemctl status redis`
        * `redis-cli ping` (should get back PONG)
        * Run `src/test_redis.py`. You should see both operations taking about 5 seconds each the first time running the script, and then almost instant the second time.
    * On Mac:
      * `brew install redis` 
      * `brew services start redis` 
        * **Note: This command launches Redis and restarts it at login.** In general Redis is a lightweight service that acts as a cache in memory, so it should have minimal performance impact.
      * If at any point you want to stop the service, do so with:
        * `brew services stop redis`
* Finally, start the Python server:
  * **FOR DEVELOPMENT:**
    * Edit `src/configs/server_configs.py` and set `CURRENT_MODE` to `AVAILABLE_MODES.DEV` instead of `AVAILABLE_MODES.PROD`
    * Inside the `src/` folder, run `python3 main.py`
    * Now if you navigate to `https://localhost:8432/docs` you should see the server's interactive page

## Logging into prod/testing server

1. Ask a dormdigest maintainer to add your public ssh key to the prod server's ssh agent
  * Example: `cat ~/.ssh/id_rsa.pub`
  * For maintainer: To check which keys are in the prod server's ssh agent already run `cat ~/.ssh/authorized_keys`
2. Access into server via ssh (after keys have been added)
  * (PROD)`ssh sipb@dormdigest.mit.edu`
  * (TESTING) `ssh root@dormdigest.xvm.mit.edu`
3. List screens that are running
  * `screen -ls`
  * For more information on screen vist: <https://vtcri.kayako.com/article/199-using-screen-in-linux-to-keep-ssh-sessions-running>
4. Connect the screen of the part of dormdigest you want to update
  * Example (to update backend): `screen -r 935.backend`
5. Kill said parts processes
  * Backend:
    * `pkill gunicorn`
    * To verify that processes have been killed
      * Check gunicorn processes: `ps aux | grep gunicorn`
      * Check server error log (should show shut down process): `cat server_error_log.txt`
    * Frontend:
      * N/A
6. Update part of dormdigest you want to update
  * Backend:
    * `git pull`
  * Frontend:
    * **FOR TESTING SERVER:**
      * Because XVM doesn't support node 18 properly, whenever you want to run a new build in production, you will need to build it locally with `npm run build` and then secure copy the build files onto the server. 
      * First, you need to make sure that the main config files in `src/server_configs.ts` and `src/auth_backend/server_configs.ts` of your local copy is representative of the XVM instance (e.g. `CURRENT_MODE` equals `AVAILABLE_MODES.TESTING`)
      * For secure copying, an example command is:
        * **For frontend:** `scp -r ~/Documents/SIPB/dormdigest-frontend/build/* root@dormdigest.xvm.mit.edu:/home/dorm/dormdigest-frontend/build/`
        * **For auth backend:** `scp -r ~/Documents/SIPB/dormdigest-frontend/auth_backend/build/* root@dormdigest.xvm.mit.edu:/home/dorm/dormdigest-frontend/auth_backend/build/`
    * **FOR PRODUCTION SERVER:**   
      * With the production server, you can just build the frontend files directly. Normally though we'll have modifications in certain config files that are specific to the production (e.g., specifying REACT_APP_BACKEND_URL and SSL cert files)
      * Because of this, you should do the following when pulling:
      * 1. `git add .`
        1. `git stash`
        2. `git pull`
        3. `git stash pop`
        4. `git reset`
        5. `git status`
      * `npm run build`
7. Get dormdigest running again
  * See the [Deployment](#deployment) section for instructions on this

## Deployment

* To run the backend, do:
  * `source env/bin/activate`
  * (Old Method) `python3 main.py 2>&1 > server_log.txt`
  * (New Method - Fault Tolerant & Multiprocessing) 
    * **FOR TESTING SERVER**
      * Inside the `src/` folder, run `run_testing.sh`
    * **FOR PRODUCTION SERVER**
      * Inside the `src/` folder, run `run_prod.sh`
* To run the authentication server, do:
  * **FOR PRODUCTION SERVER**
  * **NOTE:** As of April 10th, 2024, we've added the `--watch` flag so that the authentication server auto-restarts upon seein changes in the auth-backend files, so these steps aren't necessary for **production**. (However, you still need to do it for testing)
    * `cd ~/dormdigest-frontend/auth_backend`
    * `nvm use 18`
    * `npm install && npm run build`
    * `pm2 reload auth`
      * For documentation sake, we originally started the service with:
      * `pm2 start build/index.js --name auth --log auth_log.txt --watch`
  * **FOR TESTING SERVER**
  * **NOTE:** For some reason adding `--watch` to enable live updates on the XVM results in a restart loop, so each time you modify the auth backend build, you will also need to reload it on pm2.
    * `nvm use 16`
    * `pm2 status` (see status of jobs)
    * `pm2 reload auth`
      * For documentation sake, we originally started the service with:
      * `pm2 start build/index.js --name auth --log auth_log.txt`

## Firewall

* On the production server, we have `ufw` running, which is a firewall service that exposes specific ports that we specify to the Internet. 
  * To see which ports are open, do: `sudo ufw status`
  * To open a specific port, do: `sudo ufw allow [port_num]` 
    * This step is necessary when adding any new services to DormDigest that listens on a specific port
s
## Miscellaneous pushing / pulling from servers

* Pulling emails from mail scripts
  * In the initial stages, we're saving all emails that errored out at `mail_scripts/saved` on the dormdigest locker. To retrieve it, first log into Athena and cd into a local directory (one owned by you) folder. Then do:
    * `rsync -av /mit/dormdigest/mail_scripts/saved/ ./saved/`
  * To copy it back to your computer, do something like:
    * `scp -r kerb@athena.dialup.mit.edu:~/dormdigest/mail_scripts/saved/ ./test_emails/`
* To run the frontend static files server, do: 
  * `http-server -S -C /etc/letsencrypt/live/dormdigest.xvm.mit.edu/fullchain.pem -K /etc/letsencrypt/live/dormdigest.xvm.mit.edu/privkey.pem -p 443 ./build -- & > server_log.txt`

## Deprecated Stuff

You can ignore this part. We're saving these commands in case they become useful again in the future:

* Setup Postgres database
  * `sudo apt install postgresql postgresql-contrib`
  * `sudo -u postgres psql`
  * `CREATE DATABASE dormdigest_prod;`
