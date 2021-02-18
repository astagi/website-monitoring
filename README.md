# Website monitoring

## Run application

### Setup .env file

This file contains the environment variables

```bash
cp example.env .env
```

### Setup config.json file

This file contains rules for monitoring websites

```bash
cp example.config.json producer/config.json
```

### Start local docker

```bash
docker-compose up
```

## Development

### Install dev requirements

```bash
pip install -r requirements-dev.txt
```

### Clean Kafka topics

If you need you can clean Kafka topics inside the container running during development

```bash
kafka-topics.sh --zookeeper zookeeper:2181 --alter --topic report --config retention.ms=1000
```
