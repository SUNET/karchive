Run with:
```
$ (mkdir repo; cd repo; git init)
$ python3 main.py
```


Post data:
```
$ curl -H "Content-Type: text/plain" -X POST --data-urlencode @data.txt http://0.0.0.0:5000/commit
```
