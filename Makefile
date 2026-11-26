LUNSO ?= ../lunso-boot/build/lunso

.PHONY: all test clean

all: build/lunsoc

build/lunsoc: src/main.lunso src/lexer.lunso src/ast.lunso src/parser.lunso src/sema.lunso
	mkdir -p build
	$(LUNSO) --build src/main.lunso -o build/lunsoc

test: all
	python3 tests/run.py

clean:
	rm -rf build
