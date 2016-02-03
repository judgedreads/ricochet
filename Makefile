build:
	./setup.py build

install:
	cp misc/ricochet.desktop /usr/share/applications/
	mkdir -p /usr/share/ricochet
	cp images/* /usr/share/ricochet/
	mkdir -p /etc/ricochet
	cp misc/settings.json /etc/ricochet/
	./setup.py install

uninstall:
	rm /usr/share/applications/ricochet.desktop
	rm -r /usr/share/ricochet
	rm -r /etc/ricochet
	pip uninstall ricochet
