# lunsoc

Self-hosted compiler for the Lunso programming language.

## Requirements

- [QBE](https://c9x.me/compile/) (>= 1.3)
- [lunsoc v0.5.0](https://github.com/lunso-lang/lunsoc/releases/tag/v0.5.0) (or [lunso-boot 1.0](https://github.com/lunso-lang/lunso-boot/releases/tag/v1.0) for bootstrapping from C)
- C compiler (`cc`), `make`, `python3`

## Build & Test

```sh
make LUNSO=/path/to/lunsoc
make test LUNSO=/path/to/lunsoc
make fuzz LUNSO=/path/to/lunsoc
```

By default `Makefile` uses `LUNSO=../lunso-boot/build/lunso`.
