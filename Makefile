.PHONY: install uninstall

install:
	cp misc/ricochet.desktop /usr/share/applications/
	mkdir -p /usr/share/ricochet
	cp images/default_album.png /usr/share/ricochet/
	cp images/ricochet.svg /usr/share/icons/hicolor/scalable/apps/
	cp images/ricochet512.png /usr/share/icons/hicolor/512x512/apps/ricochet.png
	cp images/ricochet256.png /usr/share/icons/hicolor/256x256/apps/ricochet.png
	cp images/ricochet128.png /usr/share/icons/hicolor/128x128/apps/ricochet.png
	cp images/ricochet64.png /usr/share/icons/hicolor/64x64/apps/ricochet.png
	cp images/ricochet32.png /usr/share/icons/hicolor/32x32/apps/ricochet.png
	cp images/ricochet16.png /usr/share/icons/hicolor/16x16/apps/ricochet.png
	mkdir -p /etc/ricochet
	cp misc/settings.json /etc/ricochet/
	./setup.py install

uninstall:
	rm /usr/share/applications/ricochet.desktop
	rm -r /usr/share/ricochet
	rm -r /etc/ricochet
	pip uninstall ricochet
