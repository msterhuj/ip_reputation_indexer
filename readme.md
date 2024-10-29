# Ip Reputation Indexer

Get reputation of on internet and index it

## User

Build the image

```bash
docker build -t ip_repu .
```

Run the image

```bash
docker run --rm -v ./config.yml:/app/config.yml -d ip_repu
```
