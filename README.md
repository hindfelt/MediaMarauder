# MediaMarauder

A Dockerized video downloader system that processes URLs submitted via a Chrome extension. It downloads videos from supported platforms (using yt-dlp) with options for subtitles, using a Flask-based backend. The system features queue management, token-based authentication, organized storage, and automatic updates with Watchtower. 
Secured with HTTPS via Caddy, it offers seamless deployment, flexibility, and robust video processing in any Docker environment.


## API Reference

```https
  Post /{WEBHOOK_PATH defined in config.py}
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `url` | `url` | **Required**. Url to stream |
| `subtitle_lang` | `` | Language (ie 'en'/'de' etc) |


```https
  Post /{STATUS_PATH defined in config.py}
```




## Deployment

To deploy this project run

```bash

docker run -d --name mediamarauder --restart unless-stopped \
 -p 5000:5000 \
 -v /{path_to_download_mount}:/app/downloads \
 -v /{path_to_config}/config.py:/app/config.py \
 --name mediamarauder mathin/mediamarauder:latest
```

Config.py (stored outside container)
```bash
DOWNLOAD_PATH = "path"
WEBHOOK_PATH = "/{webhook-name for adding urls}"
STATUS_PATH = "/{status-hook name}"
WHITELISTED_DOMAINS = [
  "video-service.domain",
  "another-video-service.domain"
    ]
API_TOKENS = {
  "user": "token"
}

...
