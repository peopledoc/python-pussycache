# Makefile for development.
# See INSTALL and docs/dev.txt for details.
SHELL = /bin/bash
ROOT_DIR = $(shell pwd)
BIN_DIR = $(ROOT_DIR)/bin
CFG_DIR = $(ROOT_DIR)/etc
DATA_DIR = $(ROOT_DIR)/var
VIRTUALENV_DIR = $(ROOT_DIR)/lib/virtualenv
PIP = $(VIRTUALENV_DIR)/bin/pip
PROJECT = pussycache
NOSE = $(BIN_DIR)/nosetests

develop: virtualenv bin_dir directories
	$(PIP) install -r $(CFG_DIR)/virtualenv/$(PROJECT).txt


virtualenv:
	if [ ! -x $(PIP) ]; then virtualenv --no-site-packages $(VIRTUALENV_DIR); fi
	$(PIP) install -r $(CFG_DIR)/virtualenv/base.txt


bin_dir:
	if [ ! -h $(BIN_DIR) ]; then \
		ln -s $(VIRTUALENV_DIR)/bin $(BIN_DIR); \
	fi;


directories:
	mkdir -p $(DATA_DIR)/test


clean:
	find $(ROOT_DIR)/ -name "*.pyc" -delete
	find $(ROOT_DIR)/ -name ".noseids" -delete


distclean: clean
	rm -rf $(ROOT_DIR)/*.egg-info


maintainer-clean: distclean
	rm -f $(BIN_DIR)
	rm -fr $(ROOT_DIR)/lib/


test:
	$(NOSE) --config=$(CFG_DIR)/nose/base.cfg --config=$(CFG_DIR)/nose/$(PROJECT).cfg
	mv $(ROOT_DIR)/.coverage $(ROOT_DIR)/var/$(PROJECT).coverage


doc:
	make --directory=docs clean html


populate:
	cd examples/sql; sqlite3 tests.sqlite3 < populate.sql; sqlite3 tests.sqlite3 < people.sql;