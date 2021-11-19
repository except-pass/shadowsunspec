SRC = $(wildcard ./*.ipynb)
SHELL=/bin/bash -o pipefail
REPO=$(shell basename "`pwd`")

it: 
	. .venv/bin/activate && nbdev_read_nbs
	. .venv/bin/activate && nbdev_build_lib
	. .venv/bin/activate && nbdev_clean_nbs
	git status

test:
	. .venv/bin/activate && nbdev_test_nbs

readme:
	. .venv/bin/activate && nbdev_build_docs
	touch docs

clean:
	rm -rf dist

env:
	virtualenv .venv -p python3.8 --prompt "[$(REPO)] "
	. .venv/bin/activate && pip install jupyter jupyterlab nbdev
	. .venv/bin/activate && pip install -e .
ifdef WIDGET
	. .venv/bin/activate && (jupyter labextension check @jupyter-widgets/jupyterlab-manager ||  jupyter labextension install @jupyter-widgets/jupyterlab-manager)
endif

server:
	. .venv/bin/activate && jupyter lab --ip 0.0.0.0

