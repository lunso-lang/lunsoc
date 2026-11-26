# lunsoc

Self-hosted compiler for the Lunso programming language.

## Requirements

- [QBE](https://c9x.me/compile/)
- [lunsoc v0.1](https://github.com/lunso-lang/lunsoc/releases/tag/v0.1) (or [lunso-boot 1.0](https://github.com/lunso-lang/lunso-boot/releases/tag/v1.0) for bootstrapping from C)
- C compiler (`cc`), `make`, `python3`

## Build & Test

```sh
make LUNSO=/path/to/lunsoc
make test LUNSO=/path/to/lunsoc
make fuzz LUNSO=/path/to/lunsoc
```

By default `Makefile` uses `LUNSO=../lunso-boot/build/lunso`.
