# Changelog

All notable changes to `lunsoc` are documented in this file.

## [0.6.0] - 2026-11-28

### Language & Compiler
- **Tagged unions (extended `enum`)**:
  - `enum` variants can now carry payloads (`enum Value { None, Int(i64), Pair(i32, i32) }`) and generic type parameters (`enum Option[T] { Some(T), None }`).
  - `match` supports destructuring variant payloads (`Value.Int(n) => ...`), `_` wildcards (`Value.Pair(x, _) => ...`), and exhaustiveness checking.
  - Plain enums without `: backing` default to `i32` (`enum Plain { A, B }`).
- **Traits & generic bounds**:
  - Added `trait Name { ... }` declarations and `struct`/`enum` conformance lists (`struct Point : Eq, Hash`, `enum Color : u8, Eq, Hash`, `enum Value : Eq, Hash`).
  - Added generic trait bounds (`[T: Eq]`, `[K: Eq + Hash, V]`), validated on monomorphization.
  - Built-in `Eq` and `Hash` support for primitives (`i8..u64`, `bool`, and `Eq` for floats/pointers), `[]u8`/`[]const u8`, plain enums, and auto-derived `Eq`/`Hash` on structs and tagged unions (with custom `eq`/`hash` method override support).
  - Added `==` / `!=` support for `[]u8`/`[]const u8`, structs, and tagged unions implementing `Eq`.
- Adopted `0.5.1` range loops (`0..n`) and single-symbol `import std.collections.Vec` across `std/` and `src/`.

## [0.5.1] - 2026-11-28

### Breaking Changes
- **`std.collections`**: Merged `std.vec` and `std.map` into `std.collections` (`Vec[T]`, `StrMap[V]`) and removed `std/vec.lunso` and `std/map.lunso`.
- **`std/` error unions**:
  - `std.time`: `now`, `now_realtime`, `now_monotonic`, `sleep_ms` now return `!Instant` / `!void`.
  - `std.rand`: `fill_bytes(buf: []u8)`, `u64_entropy`, `init` now return `!void` / `!u64`.
  - `std.args`: `load(arena)` now returns `![][]u8`.
  - `std.json`: `parse` and `stringify` now return `!JsonValue` / `![]u8`.
  - `std.path`: `from_file_uri` and `to_file_uri` now return `![]u8`.

### Language & Compiler
- **Single-symbol imports**: Added `import mod.Symbol` (and `import mod.Symbol as Alias`) as shorthand for `import mod { Symbol }`.
- **Minimum signed integer literals**: Fixed `-128` (`i8`), `-32768` (`i16`), `-2147483648` (`i32`), and `-9223372036854775808` (`i64`) in expressions.
- **Range bound inference**: `for i in 0..n` now infers the type of `0` from `n` when `n` is typed (`i64`, `u32`, `u64`, etc.).
- Refactored `src/` to adopt `null`, `_`, `pop(null)`, and `for ... in` loops.

### Standard Library
- **`std.parse`**: Added generic `parse[T](s: []const u8): !T` using `match type T` (`bool`, `i8..i64`, `u8..u64`, `f32`, `f64`).
- **`std.collections`**: Added `Stack[T]` (`init`, `push`, `pop`, `peek`, `len`, `is_empty`, `clear`, `as_slice`).
- Modernized `std/` (`null`, `match`, `for ... in`, and implicit `!void` returns).

## [0.5.0] - 2026-11-28

### Breaking Changes
- **`std.fs`**: `read_file`, `write_file`, `copy_file`, `create_dir`, `create_dir_all`, `remove_file`, `remove_dir`, `read_dir`, `rename`, and `remove_all` now return `!T` / `!void` error unions instead of `i64` status codes with out-parameters. (`exists`, `is_dir`, and `is_file` remain `bool`.)
- **`std.process`**: `cwd`, `chdir`, `Command.init`, `Command.arg`, `Command.run`, and `Command.output` now return `!T` / `!void` error unions.
- **Unused `!T` / `!void` results**: Expression statements that evaluate to an unhandled error union now produce a compile-time error (`unused error union result; handle it with '?' or 'or'`). Use `_ = expr` to explicitly discard a result.

### Language
- **Compile-time `match type`**: `match type T { ... }` dispatches on types at compile time and type-checks/lowers only the matching arm, allowing type-specific operations inside generic functions.
- **`null` pointer literal**: Added `null` for `*T` and `*const T` pointer types (variables, constants, struct fields, function arguments, returns, casts, and `==`/`!=` comparisons).
- **Variadic `...slice` spread**: Added `...expr` in variadic function and method calls to forward an existing slice or array directly (e.g. `fmt.format(&arena, "{}={}", ...args)`).
- **Discard target `_`**: Added `_` in assignments (`_ = expr`), variable declarations (`var _ = expr`), and `for ... in` loops (`for _, v in items`, `for i, _ in items`, `for _ in 0..5`).
- **Implicit return for `!void`**: Functions returning `!void` no longer require an explicit trailing `return` when control flow reaches the end of the function body.

### Standard Library
- **`std.slice`**: Added generic slice utilities built on function pointers (`sort`, `is_sorted`, `reverse`, `fill`, `find_by`, `any_of`, `all_of`, `count_by`, `index_of`, `contains`).
- **`std/` modernization**: Adopted `Self`, method generic type inference (`arena.alloc_one`), and `for ... in` loops across `std.mem`, `std.vec`, `std.map`, `std.fmt`, `std.process`, and `std.str`.

### Compiler & Tooling
- Refactored `src/frontend` and `src/backend` to use `for ... in` loops over slices, omitted zero-initialized `Vec` fields in struct literals, and removed 454 redundant `as i64` casts in array/slice indexing.
- Added `AGENTS.md` and updated CI/release/README bootstrap target to `v0.4.0`.

## [0.4.0] - 2026-11-27

### Language
- **Error unions (`!T`, `?`, `or`, `fail(...)`)**: Added `!T` / `!void` error union return types, `?` error propagation (with `defer` execution), `or` fallback/handler blocks (`or val`, `or { ... }`, `or err { ... }`), and built-in `fail("...")`.
- **Function pointers**: Added `fun(T, ...): U` function pointer types and indirect calls.
- **Method ergonomics**: Added `Self` type alias inside `struct` methods and generic type inference for struct methods.

### Standard Library & Compiler
- Moved `format` into `std.fmt` and added `io.printf` / `io.printfln`.
- Refactored `src/driver.lunso` to use `for ... in`, `io.printfln`, `std.fs`, `std.path`, and `std.process`.
