default:
	@echo "Configuring default configuration on Router-1 and Router-2..."
	python3 network/basic_config.py
	@echo "Configured default configuration on Router-1 and Router-2"

bgp:
	@echo "Configuring BGP on Router-1 and Router-2..."
	python3 network/bgp.py
	@echo "Configured BGP on Router-1 and Router-2"

ospf:
	@echo "Configuring OSPF on Router-1 and Router-2..."
	python3 network/ospf.py
	@echo "Configured OSPF on Router-1 and Router-2"

docker:
	@echo "Building Observation Stack..."
	docker compose build 
	docker compose up -d
	@echo "Observation Stack has been built."

api:
	@echo "Building API..."
	fastapi dev agent/app.py
	@echo "API has been built."