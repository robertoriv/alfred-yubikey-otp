VERSION:=$(shell cat ./src/version)

all: clean build

build:
	cp README.md src/
	VERSION=$(VERSION) envsubst < src/info.plist.template > src/info.plist 
	cd src ; \
	zip ../Yubikey-for-Alfred-$(VERSION).alfredworkflow . -r --exclude=*.DS_Store* --exclude=*.pyc* --exclude=*.pyo* --exclude=*.plist.template*
	rm src/README.md

release:
	ghr $(VERSION) Yubikey-for-Alfred-$(VERSION).alfredworkflow

clean:
	rm -f *.alfredworkflow

update-lib:
	pip install --target src --upgrade Alfred-Workflow
	rm -rf src/Alfred_Workflow-*-info/