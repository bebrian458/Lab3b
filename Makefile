# NAME: Brian Be
# EMAIL: bebrian458@gmail.com
# UID: 204612203

DIST = lab3b lab3b.py Makefile README

default: # nothing to build

dist:
	tar -czf lab3b-204612203.tar.gz $(DIST)

clean:
	rm *tar.gz

