# LOW-LEVEL MASTERCLASS
## Assembly, Kernels, Drivers & Systems Programming

---

## 1. x86-64 ASSEMBLY

### 1.1 Fundamentals
```asm
; x86-64 System V ABI
; Registers: rax, rbx, rcx, rdx, rsi, rdi, rbp, rsp, r8-r15

; Function prologue/epilogue
push    rbp
mov     rbp, rsp
sub     rsp, 16          ; Allocate stack space
; ... function body ...
leave
ret

; Calling conventions (System V):
;   Arguments: rdi, rsi, rdx, rcx, r8, r9
;   Return: rax (or rdx:rax for 128-bit)
;   Caller-saved: rax, rcx, rdx, rsi, rdi, r8-r11
;   Callee-saved: rbp, rbx, r12-r15

; Hello World in x86-64 Linux
section .data
    hello db 'Hello, World!', 10
    hello_len equ $ - hello

section .text
    global _start
_start:
    mov     rax, 1          ; sys_write
    mov     rdi, 1          ; fd = stdout
    lea     rsi, [rel hello]
    mov     rdx, hello_len
    syscall
    
    mov     rax, 60         ; sys_exit
    xor     rdi, rdi        ; status = 0
    syscall

; 64-bit addition function
; Input: rdi = a, rsi = b
; Output: rax = a + b
add_numbers:
    mov     rax, rdi
    add     rax, rsi
    ret

; Recursive factorial
; Input: rdi = n
; Output: rax = n!
factorial:
    cmp     rdi, 1
    jle     .base
    push    rdi
    dec     rdi
    call    factorial
    pop     rdi
    imul    rax, rdi
    ret
.base:
    mov     rax, 1
    ret
```

### 1.2 System Calls
```asm
; Linux x86-64 System Calls
; rax = syscall number, args: rdi, rsi, rdx, r10, r8, r9

; sys_read(fd, buf, count)
sys_read:
    mov     rax, 0          ; sys_read
    syscall
    ret

; sys_write(fd, buf, count)
sys_write:
    mov     rax, 1          ; sys_write
    syscall
    ret

; sys_open(filename, flags, mode)
sys_open:
    mov     rax, 2          ; sys_open
    syscall
    ret

; sys_close(fd)
sys_close:
    mov     rax, 3          ; sys_close
    syscall
    ret

; sys_mmap(addr, length, prot, flags, fd, offset)
sys_mmap:
    mov     rax, 9          ; sys_mmap
    syscall
    ret

; sys_brk(addr)
sys_brk:
    mov     rax, 12         ; sys_brk
    syscall
    ret

; sys_clone(flags, stack, ptid, tls, ctid)
sys_clone:
    mov     rax, 56         ; sys_clone
    syscall
    ret

; sys_execve(path, argv, envp)
sys_execve:
    mov     rax, 59         ; sys_execve
    syscall
    ret

; sys_exit(status)
sys_exit:
    mov     rax, 60         ; sys_exit
    xor     rdi, rdi
    syscall

; Memory mapping example
mmap_example:
    mov     rax, 9          ; mmap
    xor     rdi, rdi        ; addr = NULL
    mov     rsi, 4096       ; length = page size
    mov     rdx, 7          ; PROT_READ | PROT_WRITE | PROT_EXEC
    mov     r10, 34         ; MAP_PRIVATE | MAP_ANONYMOUS
    mov     r8, -1          ; fd = -1
    mov     r9, 0           ; offset = 0
    syscall
    ret
```

### 1.3 SIMD Instructions (AVX)
```asm
; AVX-256 (Advanced Vector Extensions)
section .data
    a dq 1.0, 2.0, 3.0, 4.0
    b dq 5.0, 6.0, 7.0, 8.0
    result dq 0.0, 0.0, 0.0, 0.0

section .text
global simd_add
simd_add:
    vxorpd  ymm0, ymm0, ymm0    ; Zero ymm0
    vmovupd ymm1, [rdi]         ; Load a[]
    vmovupd ymm2, [rsi]         ; Load b[]
    vaddpd  ymm3, ymm1, ymm2   ; ymm3 = a + b
    vmovupd [rdx], ymm3         ; Store result
    vzeroupper                  ; Clear upper YMM
    ret

; Matrix multiplication (4x4) using AVX
matrix_mul_4x4:
    ; Input: rdi = A, rsi = B, rdx = C (output)
    ; Process 4x4 matrix multiplication
    ; Each iteration computes one element
    mov     rcx, 4
.loop:
    vmovups ymm0, [rdi]        ; Load row of A
    vbroadcastss ymm1, [rsi]   ; Broadcast element of B
    vmulps  ymm2, ymm0, ymm1   ; Multiply
    vaddps  ymm3, ymm3, ymm2  ; Accumulate
    add     rsi, 4
    dec     rcx
    jnz     .loop
    ret
```

---

## 2. ARM64 (AArch64) ASSEMBLY

### 2.1 Fundamentals
```asm
; ARM64 (AArch64) Assembly
; Registers: x0-x30 (64-bit), w0-w30 (lower 32 bits)
; x30 = LR (Link Register), x29 = FP (Frame Pointer)

; Function call
str     x30, [sp, #-16]!      ; Push LR
bl      function_name
ldr     x30, [sp], #16        ; Pop LR

; Return
ret

; Hello World ARM64 Linux
section .data
    hello: .ascii "Hello, World!\n"
    .equ hello_len, . - hello

section .text
.global _start
_start:
    mov     x0, 1             ; fd = stdout
    ldr     x1, =hello        ; buf
    mov     x2, hello_len     ; count
    mov     x8, 64            ; sys_write
    svc     0
    
    mov     x0, 0             ; status = 0
    mov     x8, 93            ; sys_exit
    svc     0

; ARM64 addition
; x0 = a, x1 = b -> x0 = a + b
add_64:
    add     x0, x0, x1
    ret

; ARM64 factorial
factorial:
    cmp     x0, 1
    b.le    .base
    str     x30, [sp, #-16]!  ; Save LR
    sub     x0, x0, 1
    bl      factorial
    ldr     x30, [sp], #16    ; Restore LR
    mul     x0, x0, x1
    ret
.base:
    mov     x0, 1
    ret
```

---

## 3. KERNEL DEVELOPMENT

### 3.1 Linux Kernel Module
```c
/*
 * Simple Linux Kernel Module
 * Compile: make -C /lib/modules/$(uname -r)/build M=$(pwd) modules
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Developer");
MODULE_DESCRIPTION("Simple Hello World Module");
MODULE_VERSION("1.0");

static int __init hello_init(void) {
    printk(KERN_INFO "Hello, Kernel World!\n");
    return 0;
}

static void __exit hello_exit(void) {
    printk(KERN_INFO "Goodbye, Kernel!\n");
}

module_init(hello_init);
module_exit(hello_exit);
```

### 3.2 Character Device Driver
```c
/*
 * Character Device Driver
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>

#define DEVICE_NAME "mychardev"
#define CLASS_NAME "myclass"

static int major_number;
static struct class *device_class = NULL;
static struct device *device_struct = NULL;
static char kernel_buffer[256];

static int dev_open(struct inode *inode, struct file *file) {
    printk(KERN_INFO "Device opened\n");
    return 0;
}

static int dev_release(struct inode *inode, struct file *file) {
    printk(KERN_INFO "Device closed\n");
    return 0;
}

static ssize_t dev_read(struct file *file, char __user *user_buffer, 
                        size_t len, loff_t *offset) {
    int bytes_read = 0;
    
    if (*offset > 0)
        return 0;
    
    bytes_read = strlen(kernel_buffer);
    if (copy_to_user(user_buffer, kernel_buffer, bytes_read))
        return -EFAULT;
    
    *offset = bytes_read;
    printk(KERN_INFO "Read %d bytes\n", bytes_read);
    return bytes_read;
}

static ssize_t dev_write(struct file *file, const char __user *user_buffer,
                         size_t len, loff_t *offset) {
    if (len > 255)
        len = 255;
    
    if (copy_from_user(kernel_buffer, user_buffer, len))
        return -EFAULT;
    
    kernel_buffer[len] = '\0';
    printk(KERN_INFO "Wrote %zu bytes\n", len);
    return len;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = dev_open,
    .release = dev_release,
    .read = dev_read,
    .write = dev_write,
};

static int __init char_driver_init(void) {
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        printk(KERN_ALERT "Failed to register device\n");
        return major_number;
    }
    
    device_class = class_create(THIS_MODULE, CLASS_NAME);
    device_struct = device_create(device_class, NULL, 
                                   MKDEV(major_number, 0), 
                                   NULL, DEVICE_NAME);
    
    printk(KERN_INFO "Device registered with major %d\n", major_number);
    return 0;
}

static void __exit char_driver_exit(void) {
    device_destroy(device_class, MKDEV(major_number, 0));
    class_destroy(device_class);
    unregister_chrdev(major_number, DEVICE_NAME);
    printk(KERN_INFO "Device unregistered\n");
}

module_init(char_driver_init);
module_exit(char_driver_exit);
MODULE_LICENSE("GPL");
```

### 3.3 Kernel Synchronization
```c
/*
 * Kernel Synchronization Primitives
 */
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include <linux/completion.h>
#include <linux/kthread.h>

// Mutex (sleepable)
static DEFINE_MUTEX(my_mutex);

void mutex_example(void) {
    mutex_lock(&my_mutex);
    // Critical section
    mutex_unlock(&my_mutex);
}

// Spinlock (non-sleepable)
static DEFINE_SPINLOCK(my_spinlock);

void spinlock_example(unsigned long flags) {
    spin_lock_irqsave(&my_spinlock, flags);
    // Critical section
    spin_unlock_irqrestore(&my_spinlock, flags);
}

// Atomic operations
static atomic_t counter = ATOMIC_INIT(0);

void atomic_example(void) {
    atomic_inc(&counter);
    atomic_add(5, &counter);
    int val = atomic_read(&counter);
    atomic_dec_and_test(&counter);
}

// RCU (Read-Copy-Update)
void rcu_read_example(void) {
    rcu_read_lock();
    // Read data structure
    rcu_read_unlock();
}

void rcu_write_example(void) {
    struct my_data *new, *old;
    new = kmalloc(sizeof(*new), GFP_KERNEL);
    // Initialize new
    rcu_assign_pointer(ptr, new);
    synchronize_rcu();  // Wait for readers
    kfree(old);
}

// Completion
static DECLARE_COMPLETION(done);

void completion_example(void) {
    wait_for_completion(&done);
}

void completion_signal(void) {
    complete(&done);
}

// Workqueue
static void work_handler(struct work_struct *work) {
    printk(KERN_INFO "Work executed\n");
}

static DECLARE_WORK(work, work_handler);

void workqueue_example(void) {
    schedule_work(&work);
}
```

### 3.4 Memory Management
```c
/*
 * Kernel Memory Management
 */
#include <linux/mm.h>
#include <linux/slab.h>

// kmalloc (physical contiguous memory)
void *buf = kmalloc(4096, GFP_KERNEL);
if (buf)
    memset(buf, 0, 4096);
kfree(buf);

// vmalloc (virtually contiguous)
void *vbuf = vmalloc(4096);
vfree(vbuf);

// Page allocation
struct page *page = alloc_pages(GFP_KERNEL, 0);  // 2^0 = 1 page
void *p = page_address(page);
__free_pages(page, 0);

// Slab allocator
struct kmem_cache *cache = kmem_cache_create("my_cache", 
                                              sizeof(struct my_struct),
                                              0, SLAB_HWCACHE_ALIGN, NULL);
struct my_struct *obj = kmem_cache_alloc(cache, GFP_KERNEL);
kmem_cache_free(cache, obj);
kmem_cache_destroy(cache);

// get_free_pages
unsigned long order = 2;  // 2^2 = 4 pages
unsigned long *pages = __get_free_pages(GFP_KERNEL, order);
free_pages((unsigned long)pages, order);

// Memory mapping
int remap_pfn_range(struct vm_area_struct *vma,
                    unsigned long virt_addr,
                    unsigned long pfn,
                    unsigned long size,
                    pgprot_t prot);

#include <linux/io.h>
void *io_mem = ioremap_nocache(0xFFE00000, 4096);
iounmap(io_mem);
```

---

## 4. BOOTLOADERS

### 4.1 Simple Bootloader
```asm
; Simple x86 Bootloader (16-bit mode)
[BITS 16]
ORG 0x7C00

start:
    mov ax, 0x0000
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    
    ; Clear screen
    mov ah, 0x07
    mov al, 0
    mov bh, 0x07
    mov cx, 0
    mov dh, 24
    mov dl, 79
    int 0x10
    
    ; Set cursor
    mov ah, 0x02
    mov bh, 0
    mov dh, 0
    mov dl, 0
    int 0x10
    
    ; Print message
    mov si, message
    mov ah, 0x0E
.print_loop:
    lodsb
    or al, al
    jz .done
    int 0x10
    jmp .print_loop
.done:
    jmp $

message db 'Hello from Bootloader!', 0

times 510-($-$$) db 0
dw 0xAA55
```

---

## 5. REALTIME SYSTEMS

### 5.1 RTOS Concepts
```c
/*
 * FreeRTOS Example
 */
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

static QueueHandle_t xQueue;

void vTaskSender(void *pvParameters) {
    TickType_t xTick = pdMS_TO_TICKS(100);
    int counter = 0;
    
    while (1) {
        xQueueSend(xQueue, &counter, 0);
        counter++;
        vTaskDelay(xTick);
    }
}

void vTaskReceiver(void *pvParameters) {
    int received;
    TickType_t xTick = pdMS_TO_TICKS(200);
    
    while (1) {
        if (xQueueReceive(xQueue, &received, portMAX_DELAY)) {
            printf("Received: %d\n", received);
        }
        vTaskDelay(xTick);
    }
}

void main(void) {
    xQueue = xQueueCreate(10, sizeof(int));
    
    xTaskCreate(vTaskSender, "Sender", 1000, NULL, 1, NULL);
    xTaskCreate(vTaskReceiver, "Receiver", 1000, NULL, 1, NULL);
    
    vTaskStartScheduler();
}
```

### 5.2 Interrupt Handling
```asm
; ARM64 Interrupt Handler
.global irq_handler
irq_handler:
    ; Save context
    sub     sp, sp, #256
    stp     x0, x1, [sp, #0]
    stp     x2, x3, [sp, #16]
    stp     x4, x5, [sp, #32]
    stp     x6, x7, [sp, #48]
    stp     x8, x9, [sp, #64]
    stp     x10, x11, [sp, #80]
    stp     x12, x13, [sp, #96]
    stp     x14, x15, [sp, #112]
    stp     x16, x17, [sp, #128]
    stp     x18, x19, [sp, #144]
    stp     x20, x21, [sp, #160]
    stp     x22, x23, [sp, #176]
    stp     x24, x25, [sp, #192]
    stp     x26, x27, [sp, #208]
    stp     x28, x29, [sp, #224]
    str     x30, [sp, #240]
    
    ; Call C interrupt handler
    bl      handle_interrupt
    
    ; Restore context
    ldp     x0, x1, [sp, #0]
    ldp     x2, x3, [sp, #16]
    ldp     x4, x5, [sp, #32]
    ldp     x6, x7, [sp, #48]
    ldp     x8, x9, [sp, #64]
    ldp     x10, x11, [sp, #80]
    ldp     x12, x13, [sp, #96]
    ldp     x14, x15, [sp, #112]
    ldp     x16, x17, [sp, #128]
    ldp     x18, x19, [sp, #144]
    ldp     x20, x21, [sp, #160]
    ldp     x22, x23, [sp, #176]
    ldp     x24, x25, [sp, #192]
    ldp     x26, x27, [sp, #208]
    ldp     x28, x29, [sp, #224]
    ldr     x30, [sp, #240]
    
    add     sp, sp, #256
    eret
```

---

## 6. PERFORMANCE OPTIMIZATION

### 6.1 Cache Optimization
```c
/*
 * CPU Cache Optimization Techniques
 */

// Data layout - Structure of Arrays (SoA) vs Array of Structures (AoS)
struct PointAoS { float x, y, z; };      // Cache-unfriendly
struct PointSoA { float x[N], y[N], z[N]; };  // Cache-friendly

// Cache line aware allocation
#define CACHE_LINE 64
struct aligned_data {
    char data[64];
} __attribute__((aligned(CACHE_LINE)));

// Prefetching
void prefetch_example(float *src, float *dst, int n) {
    for (int i = 0; i < n; i++) {
        __builtin_prefetch(&src[i + 8], 0, 3);  // Prefetch 8 ahead
        dst[i] = src[i] * 2.0f;
    }
}

// Loop tiling/blocking for cache efficiency
void matmul_blocked(float *A, float *B, float *C, int N, int block) {
    for (int i = 0; i < N; i += block) {
        for (int j = 0; j < N; j += block) {
            for (int k = 0; k < N; k += block) {
                for (int ii = i; ii < min(i+block, N); ii++) {
                    for (int jj = j; jj < min(j+block, N); jj++) {
                        for (int kk = k; kk < min(k+block, N); kk++) {
                            C[ii*N + jj] += A[ii*N + kk] * B[kk*N + jj];
                        }
                    }
                }
            }
        }
    }
}

// Branchless programming
int branchless_max(int a, int b) {
    int diff = a - b;
    int sign = diff >> 31;  // -1 if negative, 0 if positive
    return a - (diff & sign);
}
```

### 6.2 SIMD Optimization
```c
/*
 * SIMD Optimization with Intrinsics
 */
#include <immintrin.h>

// AVX2 vectorized addition
void add_arrays_avx(float *a, float *b, float *c, int n) {
    for (int i = 0; i < n; i += 8) {
        __m256 va = _mm256_loadu_ps(&a[i]);
        __m256 vb = _mm256_loadu_ps(&b[i]);
        __m256 vc = _mm256_add_ps(va, vb);
        _mm256_storeu_ps(&c[i], vc);
    }
}

// AVX2 dot product
float dot_product_avx(float *a, float *b, int n) {
    __m256 sum = _mm256_setzero_ps();
    
    for (int i = 0; i < n; i += 8) {
        __m256 va = _mm256_loadu_ps(&a[i]);
        __m256 vb = _mm256_loadu_ps(&b[i]);
        sum = _mm256_fmadd_ps(va, vb, sum);  // multiply-add
    }
    
    float result[8];
    _mm256_storeu_ps(result, sum);
    return result[0] + result[1] + result[2] + result[3] +
           result[4] + result[5] + result[6] + result[7];
}

// NEON (ARM) example
#ifdef __ARM_NEON
#include <arm_neon.h>

float32x4_t neon_add(float32x4_t a, float32x4_t b) {
    return vaddq_f32(a, b);
}
#endif
```

---

## 7. BARE METAL PROGRAMMING

### 7.1 Raspberry Pi Bare Metal
```c
/*
 * Raspberry Pi 3/4 Bare Metal
 */

// MMU Setup
void enable_mmu(void) {
    // Configure translation table
    volatile unsigned int *table = (unsigned int *)0x4000;
    
    // Identity mapping: 1GB (0x00000000 - 0x3FFFFFFF)
    for (int i = 0; i < 4096; i++) {
        // Normal memory, inner/outer write-back
        table[i] = (i << 20) | 0x15C0E;  // | (i<<20);
    }
    
    // Set translation table base
    asm volatile("msr ttbr0_el1, %0" : : "r"(0x4000));
    
    // Enable MMU
    unsigned long sctlr;
    asm volatile("mrs %0, sctlr_el1" : "=r"(sctlr));
    sctlr |= 1;  // Enable MMU
    asm volatile("msr sctlr_el1, %0" : : "r"(sctlr));
}

// UART
void uart_init(void) {
    volatile unsigned int *gpio = (unsigned int *)0x3F200000;
    volatile unsigned int *uart = (unsigned int *)0x3F215000;
    
    // Set GPIO 14, 15 to alt function 0 (UART0)
    gpio[1] = (gpio[1] & ~0xF000) | 0x4000;
    gpio[1] = (gpio[1] & ~0xF) | 0x400;
    
    // Enable UART
    uart[1] = 0;           // Disable during config
    uart[3] = 0x70;        // 8-bit, enable FIFO
    uart[1] = 0x3;         // Enable TX/RX
}

void uart_putc(char c) {
    volatile unsigned int *uart = (unsigned int *)0x3F215000;
    while (uart[5] & 0x20);  // Wait TX empty
    uart[0] = c;
}
```

---

## 8. REVERSING & DEBUGGING

### 8.1 GDB Scripts
```gdb
# GDB useful commands

# Breakpoint with condition
break main if argc > 1

# Watchpoint
watch *0x08049000
rwatch *0x08049000
awatch *0x08049000

# Examine memory
x/20x 0x08048000    # 20 words in hex
x/10i 0x08048000    # 10 instructions
x/s 0x08048000      # string

# Disassembly
disassemble main
set disassembly-flavor intel

# Register manipulation
info registers
set $eax = 0

# Stack examination
info frame
backtrace
info locals

# Continue with conditions
handle SIGSEGV nopass print nostop

# Custom command
define hook-stop
    printf "EIP: 0x%x\n", $eip
end

# Pattern generation for buffer overflow
pattern create 100
pattern offset $esp
```

### 8.2 objdump analysis
```bash
# Disassemble
objdump -d program

# Show symbols
objdump -t program

# Show relocations
objdump -r program

# Show headers
objdump -h program

# Full analysis
readelf -a program

# Check security
checksec --file=program
```

---

*End of Low-Level Masterclass*
