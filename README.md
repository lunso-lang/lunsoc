# lunsoc

Self-hosted compiler for the Lunso programming language.

## Requirements

- [QBE](https://c9x.me/compile/)
- [lunso-boot 1.0](https://github.com/lunso-lang/lunso-boot/releases/tag/v1.0)
- C compiler (`cc`), `make`, `python3`

## Build & Test

```sh
make
make test
make fuzz
```

By default `Makefile` expects `lunso-boot` at `../lunso-boot/build/lunso`. Override with `LUNSO=/path/to/lunso`.
