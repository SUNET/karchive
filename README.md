KArchive
---------

Webserver and backend which accepts PUT requests to store files in Git
repositories. Intended to use together with JunOS archive.

### Install:

The environment variable `GIT_REPO_URL` must be set to the path of the git:

### Configure JunOS:

```
admin@foo-bar# set system archival configuration archive-sites http://qanon@109.105.11.11/commit
```

### Test with CURL:

```
$ curl -X PUT -H'Content-Type: application/gzip' --data-binary @data.conf.gz https://localhost/commit/data.conf.gz
```
