all: clean build

build:
	cp README.md src/
	cd src ; \
	zip ../Yubikey-for-Alfred.alfredworkflow . -r --exclude=*.DS_Store* --exclude=*.pyc* --exclude=*.pyo*
	rm src/README.md

clean:
	rm -f *.alfredworkflow

update-lib:
	pip install --target src --upgrade Alfred-Workflow
	rm -rf src/Alfred_Workflow-*-info/