# Sanitizing emails

For purposes of user privacy, sanitize the emails before committing/pushing them.

If there are more types of information we should be scrubbing, please let us know.

## Domain names

* Replace domains with "domain.com"
* Note uppercase domains
* Keep subdomains the same (e.g. "scripts.domain.com")

## Users

* Replace email **usernames** with "username"
* Replace **names** with "Firstname Lastname"

## Links

* Remove personally identifying **links** ("[LINK REDACTED]")

## Double check!

* Check HTML content for everything above
* Do the same for any **base 64**-encoded content