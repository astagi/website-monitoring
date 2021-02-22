clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf

integration-test: clean
	@mv producer/config.json producer/back_config.json || true
	@cp example.config.json producer/config.json
	@docker-compose up -d --build
	@mv producer/back_config.json producer/config.json || true
	@python integration_tests.py
	@docker-compose down

test: clean
	@docker-compose up -d db zookeeper kafka
	@flake8 consumer producer
	@sleep 10
	@pytest --cov=consumer --cov=producer . -s
	@docker-compose down
