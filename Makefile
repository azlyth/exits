.PHONY = build run
PROJECT_NAME = subway-exit-data

all: build run

build:
	@docker build -t $(PROJECT_NAME) image/

shell:
	@docker run --rm -it -v $(shell pwd)/data:/data $(PROJECT_NAME) sh

silent-build:
	@docker build -t $(PROJECT_NAME) image/ >/dev/null 2>&1

keep-running:
	@#Relies on the vim-hook script to write to output.txt
	@watch -n0.5 cat output.txt

map-geojson:
	@docker run --rm -v $(shell pwd)/data:/data $(PROJECT_NAME) map-geojson

frontend-json:
	@docker run --rm -v $(shell pwd)/data:/data $(PROJECT_NAME) frontend-json
