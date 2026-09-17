## About
This is a simple image-displaying web server built with FastAPI, designed for previewing images on servers without a graphical user interface (GUI).


## How To use.
#### Option 1.run direct

set base directory at `BASE_DIR = Path("./logs").resolve()`, line 10 in main.py

run server
```
pip install -r requirements.txt
uvicorn main:app --host=0.0.0.0 --port=8080
```

#### Option 2.run with docker

we don't need set base directory in code, just map your directory to `/app/logs` with docker
```
# image build
docker build . -t simple-media-gallary:latest

# docker run, set your directory
docker run docker run -itd \
  --name image-log-viewer \
  -p 8080:8080 \
  -v /home/devserver/logs:/app/logs \
  simple-media-gallary:latest
```

## Tips
#### image url copy

Due to the strict restrictions of "Secure Contexts," the image URL copying function does not work in an HTTP environment; switching to a self-signed SSL certificate resolves this issue. got self-signed SSL certificate with [mkcert](https://github.com/FiloSottile/mkcert)

``` 