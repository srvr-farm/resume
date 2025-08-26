

ifndef BUILD_NUMBER
	BUILD_NUMBER=local
endif

ifndef VERSION
	VERSION=1.0
endif

BUILD_TAG="$(VERSION).$(BUILD_NUMBER)"

.PHONY: certs config docker compiler venv

web: html css

compiler: venv
venv: venv/bin/activate
venv/bin/activate:
	virtualenv -p python3 venv
	. venv/bin/activate ; pip install --upgrade pip
	. venv/bin/activate ; pip install -r compiler/requirements.txt

target:
	mkdir target

css: target/html/css
target/html/css: target
	cp -R web/css target/html

html: compiler target/html
target/html: target
	mkdir -p target/html
	. venv/bin/activate ; ./compiler/compile.py web/resume target/html
	cp -R web/css target/html

install:
	mkdir -p /srv/resume/html /srv/resume/conf.d /opt/resume/bin
	cp -R target/html/* /srv/resume/html
	cp -R service/srv/resume/conf.d/* /srv/resume/conf.d
	cp -R service/opt/resume/bin/* /opt/resume/bin
	chmod +x /opt/resume/bin/*
	cp service/usr/lib/systemd/system/resume.service /usr/lib/systemd/system/
	systemctl daemon-reload
	systemd-analyze verify /usr/lib/systemd/system/resume.service && sudo systemctl enable resume.service && systemctl restart resume.service


clean:
	rm -rf target

