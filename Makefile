VERSION:=$(shell cat ./src/version)

all: clean build

build: requirements
	cp README.md src/
	VERSION=$(VERSION) envsubst < src/info.plist.template > src/info.plist
	cd src ; \
	zip ../Yubikey-for-Alfred-v$(VERSION).alfredworkflow . -r --exclude=*.DS_Store* --exclude=*.pyc* --exclude=*.pyo* --exclude=*.plist.template*
	rm src/README.md src/info.plist

release: build
	ghr v$(VERSION) Yubikey-for-Alfred-v$(VERSION).alfredworkflow

clean:
	rm -f *.alfredworkflow

requirements:
	pip install --target src --upgrade Alfred-Workflow packaging
	rm -rf src/Alfred_Workflow-*-info/
