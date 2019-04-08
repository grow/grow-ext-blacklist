SHELL := /bin/bash
PATH := $(PATH):$(HOME)/bin

test:
	grow install example
	@echo Staging should build normally:
	grow deploy staging
	@echo Prod should fail due to blacklist:
	grow deploy prod
