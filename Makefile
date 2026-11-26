LUNSO ?= ../lunso-boot/build/lunso

.PHONY: all test clean

all: build/lunsoc

build/lunsoc: src/main.lunso src/lexer.lunso
	mkdir -p build
	$(LUNSO) --build src/main.lunso -o build/lunsoc

test: all
	python3 tests/run.py

clean:
	rm -rf build
