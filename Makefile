clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf

integration-test: clean
	@docker-compose up -d db zookeeper kafka
	@flake8 consumer producer
	@sleep 10

test: clean
	@docker-compose up -d db zookeeper kafka
	@flake8 consumer producer
	@sleep 10
	@pytest --cov=consumer --cov=producer . -s
	@docker-compose down
