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

We set up auto cert renew by running `crontab -e` and then adding the following line:

```text
0 12 * * * /snap/bin/certbot renew --quiet --nginx
```

This should run certbot every day to check if we need to renew our certificate and then renew as necessary.