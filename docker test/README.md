# Hello World Flask App (Dockerized)

## Build the Docker image

```sh
docker build -t hello-flask .
```

## Run the Docker container on a random port

```sh
docker run -d -p 0:5000 hello-flask
```

Or, to see which port was assigned:

```sh
docker run -d -P hello-flask
```

Then check the mapped port with:

```sh
docker ps
```

Visit `http://localhost:<PORT>` in your browser. 