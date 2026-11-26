LUNSO ?= ../lunso-boot/build/lunso
FUZZ_ITERS ?= 20000

.PHONY: all test fuzz clean

all: build/lunsoc

build/lunsoc: src/main.lunso src/lexer.lunso src/ast.lunso src/parser.lunso src/modules.lunso src/sema.lunso src/ir.lunso src/qbe.lunso src/native.lunso
	mkdir -p build
	$(LUNSO) --build src/main.lunso -o build/lunsoc

test: all
	python3 tests/run.py

build/fuzz: all src/fuzz.lunso
	./build/lunsoc --build src/fuzz.lunso -o build/fuzz

fuzz: build/fuzz
	./build/fuzz --iters=$(FUZZ_ITERS) src/*.lunso ../lunso-boot/tests/pass/*.lunso

clean:
	rm -rf build
