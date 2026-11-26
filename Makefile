CC ?= cc
LUNSO ?= ../lunso-boot/build/lunso
FUZZ_ITERS ?= 20000
FUZZ_SEEDS := src/*.lunso src/frontend/*.lunso $(wildcard tests/pass/*.lunso ../lunso-boot/tests/pass/*.lunso)

.PHONY: all test fuzz clean

all: build/lunsoc build/std-linux-x86_64.o

build/std-linux-x86_64.o: std/platform/linux_x86_64.s
	mkdir -p build
	$(CC) $(ASFLAGS) -c $< -o $@

build/lunsoc: src/main.lunso src/driver.lunso src/frontend/lexer.lunso src/frontend/ast.lunso src/frontend/parser.lunso src/frontend/modules.lunso src/frontend/sema.lunso src/ir.lunso src/qbe.lunso src/native.lunso build/std-linux-x86_64.o
	mkdir -p build
	LUNSO_STD_OBJ=$(CURDIR)/build/std-linux-x86_64.o $(LUNSO) --build --std $(CURDIR)/std src/main.lunso -o build/lunsoc

test: all
	python3 tests/run.py

build/fuzz: all tests/fuzz.lunso
	LUNSO_STD_OBJ=$(CURDIR)/build/std-linux-x86_64.o ./build/lunsoc --build -I $(CURDIR)/src --std $(CURDIR)/std tests/fuzz.lunso -o build/fuzz

fuzz: build/fuzz
	./build/fuzz --iters=$(FUZZ_ITERS) $(FUZZ_SEEDS)

clean:
	rm -rf build
