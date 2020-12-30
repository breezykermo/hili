# Python client for hili
A simple Python script with no dependencies to clip to a hili server. It reads
arguments from a `.txt` file, and will default to looking for '/tmp/args.txt' if
you don't specify an argument file. If you're offline at the time of clip, it'll
store it on disk, and retry next time you try to clip with the script.

Clip the example.txt to a hili server using the following command:

```
URL=http://localhost:8888 ARGS=example.txt python clip.py
```

