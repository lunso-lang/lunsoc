.text
.globl lunso_sys_read
.type lunso_sys_read, @function
lunso_sys_read:
    xor %eax, %eax
    syscall
    ret
.size lunso_sys_read, .-lunso_sys_read

.globl lunso_sys_write
.type lunso_sys_write, @function
lunso_sys_write:
    mov $1, %eax
    syscall
    ret
.size lunso_sys_write, .-lunso_sys_write

.globl lunso_sys_file_open
.type lunso_sys_file_open, @function
lunso_sys_file_open:
    mov $02000000, %edx     # O_CLOEXEC | O_RDONLY
    test %sil, %sil
    jz .Lfile_open
    or $01101, %edx         # O_WRONLY | O_CREAT | O_TRUNC
.Lfile_open:
    mov %rdi, %rsi          # path
    mov $-100, %edi         # AT_FDCWD
    mov $0666, %r10d        # creation mode, filtered by umask
    mov $257, %eax          # openat
    syscall
    ret
.size lunso_sys_file_open, .-lunso_sys_file_open

.globl lunso_sys_file_close
.type lunso_sys_file_close, @function
lunso_sys_file_close:
    mov $3, %eax            # close
    syscall
    ret
.size lunso_sys_file_close, .-lunso_sys_file_close

.globl lunso_mem_map
.type lunso_mem_map, @function
lunso_mem_map:
    push %rsi
    mov %rdi, %rsi
    xor %edi, %edi
    mov $3, %edx           # PROT_READ | PROT_WRITE
    mov $0x22, %r10d       # MAP_PRIVATE | MAP_ANONYMOUS
    mov $-1, %r8
    xor %r9d, %r9d
    mov $9, %eax           # mmap
    syscall
    pop %rdx
    cmp $-4095, %rax
    jae .Lmap_done
    mov %rax, (%rdx)
    xor %eax, %eax
.Lmap_done:
    ret
.size lunso_mem_map, .-lunso_mem_map

.globl lunso_mem_unmap
.type lunso_mem_unmap, @function
lunso_mem_unmap:
    mov $11, %eax          # munmap
    syscall
    ret
.size lunso_mem_unmap, .-lunso_mem_unmap

.globl lunso_sys_fork
.type lunso_sys_fork, @function
lunso_sys_fork:
    mov $57, %eax          # fork
    syscall
    ret
.size lunso_sys_fork, .-lunso_sys_fork

.globl lunso_sys_execve
.type lunso_sys_execve, @function
lunso_sys_execve:
    mov $59, %eax          # execve
    syscall
    ret
.size lunso_sys_execve, .-lunso_sys_execve

.globl lunso_sys_exit
.type lunso_sys_exit, @function
lunso_sys_exit:
    mov $60, %eax          # exit
    syscall
.size lunso_sys_exit, .-lunso_sys_exit

.globl lunso_sys_wait4
.type lunso_sys_wait4, @function
lunso_sys_wait4:
    xor %edx, %edx         # options = 0
    xor %r10d, %r10d       # rusage = NULL
    mov $61, %eax          # wait4
    syscall
    ret
.size lunso_sys_wait4, .-lunso_sys_wait4

.globl lunso_sys_access
.type lunso_sys_access, @function
lunso_sys_access:
    mov $21, %eax          # access
    syscall
    ret
.size lunso_sys_access, .-lunso_sys_access

.globl lunso_sys_mkdir
.type lunso_sys_mkdir, @function
lunso_sys_mkdir:
    mov %rdi, %rsi         # pathname
    mov $-100, %edi        # AT_FDCWD
    mov $0755, %edx        # mode
    mov $258, %eax         # mkdirat
    syscall
    ret
.size lunso_sys_mkdir, .-lunso_sys_mkdir

.globl lunso_sys_unlink
.type lunso_sys_unlink, @function
lunso_sys_unlink:
    mov %esi, %edx         # flags (0 or AT_REMOVEDIR)
    mov %rdi, %rsi         # pathname
    mov $-100, %edi        # AT_FDCWD
    mov $263, %eax         # unlinkat
    syscall
    ret
.size lunso_sys_unlink, .-lunso_sys_unlink

.globl lunso_sys_clock_gettime
.type lunso_sys_clock_gettime, @function
lunso_sys_clock_gettime:
    mov %rsi, %r8          # save out_sec
    mov %rdx, %r9          # save out_nsec
    sub $16, %rsp          # struct timespec { i64 tv_sec; i64 tv_nsec; }
    mov %rsp, %rsi
    mov $228, %eax         # clock_gettime
    syscall
    test %rax, %rax
    js .Lclock_done
    test %r8, %r8
    jz .Lclock_nsec
    mov (%rsp), %rcx
    mov %rcx, (%r8)
.Lclock_nsec:
    test %r9, %r9
    jz .Lclock_done
    mov 8(%rsp), %rcx
    mov %rcx, (%r9)
.Lclock_done:
    add $16, %rsp
    ret
.size lunso_sys_clock_gettime, .-lunso_sys_clock_gettime

.globl lunso_sys_nanosleep
.type lunso_sys_nanosleep, @function
lunso_sys_nanosleep:
    push %rsi              # tv_nsec
    push %rdi              # tv_sec
    mov %rsp, %rdi         # req
    xor %esi, %esi         # rem = NULL
    mov $35, %eax          # nanosleep
    syscall
    add $16, %rsp
    ret
.size lunso_sys_nanosleep, .-lunso_sys_nanosleep

.globl lunso_sys_getrandom
.type lunso_sys_getrandom, @function
lunso_sys_getrandom:
    mov $318, %eax         # getrandom
    syscall
    ret
.size lunso_sys_getrandom, .-lunso_sys_getrandom

.section .note.GNU-stack,"",@progbits
