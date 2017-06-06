# NAME: Brian Be, Leslie Liang
# EMAIL: bebrian458@gmail.com, lliang9838@gmail.com
# ID: 204612203, 204625818

DIST = lab3b lab3b.py Makefile README

default:
	chmod +x lab3b

dist:
	tar -czf lab3b-204612203.tar.gz $(DIST)

clean:
	rm *tar.gz

