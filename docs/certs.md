# Certificates

We currently have Let's Encrypt SSL certificates. They are integrated in the Nginx server configuration, and we also renew them through the `--nginx` flag. However, it's important to note that these certificates are also shared by the backend Python server *and* the Express auth server.

## Installation

```sh
rm /etc/nginx/sites-available/default
ln -s /etc/nginx/sites-available/dormdigest /etc/nginx/sites-enabled
certbot --nginx -d dormdigest.xvm.mit.edu
sudo systemctl restart nginx
```

## Auto-Renew


### For Production Server

Because we need to be running as root to renew the certificates, we'll be editing the crontab of the root user. We set up auto cert renew by running `sudo crontab -e` and then adding the following line:

```text
0 12 * * * certbot renew --quiet --nginx; chgrp -R sipb /etc/letsencrypt; chmod -R g=rX /etc/letsencrypt
```

This should run certbot every day to check if we need to renew our certificate and then renew as necessary. 

**Note:** On the production server, since we're using a `sipb` user instead of `root`, we needed to modify the permissions of files in the LetsEncrypt cert folder so that processes/services running as `sipb` can access it:

```sh
sudo chgrp -R sipb /etc/letsencrypt/
sudo chmod -R g=rX /etc/letsencrypt/
```

References:
0. <https://community.letsencrypt.org/t/how-to-use-certs-in-non-root-services/2690/4>
1. <https://stackoverflow.com/questions/64411875/what-is-the-most-secure-way-to-use-lets-encrypt-certificates-with-node-js>

We believe these permissions should be preserved across renewals, but the commands are also run after the `certbot renew` command inside the crontab in case it's necessary.

### For Testing server

Since everything is running as root, we can just do `crontab -e`, and add the line:

```text
0 12 * * * /snap/bin/certbot renew --quiet --nginx
```