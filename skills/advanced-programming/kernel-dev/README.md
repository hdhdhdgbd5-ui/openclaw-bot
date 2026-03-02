# 🖥️ Operating System Kernel Development

**Build the foundation of all software**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **Custom OS** | Embedded/specialized systems | $100K-500K |
| **Hypervisors** | Virtualization | $150K-500K |
| **Device Drivers** | Hardware interfaces | $50K-300K |
| **RTOS** | Real-time systems | $100K-400K |
| **Containers** | Isolation runtime | $50K-200K |

---

## 📚 Learning Path

### Week 1: Kernel Basics
1. Assembly (x86-64)
2. Boot process
3. Memory management
4. Interrupt handling

### Week 2: Core Systems
1. Process/thread management
2. System calls
3. File systems
4. Virtual memory

### Week 3: Advanced
1. Kernel synchronization
2. Scheduling algorithms
3. Device drivers
4. Virtualization

### Week 4: Projects
1. Simple OS (TutorialOS)
2. Shell
3. File system
4. Simple driver

---

## 💻 Minimal x86-64 Kernel

### Boot Sector
```asm
; Simple boot sector - boot.asm
[BITS 16]
[ORG 0x7C00]

; Simple bootloader that loads kernel
start:
    mov ax, 0x07E0      ; Load to 0x0000:0x7E00
    mov ds, ax
    mov es, ax
    mov bx, 0           ; Offset
    
    mov ah, 0x02        ; Read disk sector
    mov al, 10          ; Sectors to read
    mov ch, 0           ; Cylinder
    mov cl, 2           ; Start sector (after boot sector)
    mov dh, 0           ; Head
    mov dl, 0x80        ; First hard drive
    int 0x13
    
    jc disk_error
    
    jmp 0x0000:0x7E00   ; Jump to kernel
    
disk_error:
    mov si, error_msg
    call print_string
    jmp $
    
print_string:
    lodsb
    or al, al
    jz done
    mov ah, 0x0E
    int 0x10
    jmp print_string
done:
    ret
    
error_msg db 'Disk error!', 0

times 510-($-$$) db 0
dw 0xAA55
```

### Kernel Entry Point
```c
// kernel.c - Simple C kernel
#include <stdint.h>

// VGA text mode
volatile uint16_t* vga_buffer = (uint16_t*)0xB8000;
int vga_index = 0;

void print(const char* str) {
    for (int i = 0; str[i]; i++) {
        vga_buffer[vga_index++] = (0x0F << 8) | str[i];
    }
}

void print_hex(uint64_t num) {
    char hex[] = "0123456789ABCDEF";
    char buf[17];
    for (int i = 0; i < 16; i++) {
        buf[15-i] = hex[num & 0xF];
        num >>= 4;
    }
    buf[16] = 0;
    print(buf);
}

// IDT setup
struct idt_entry {
    uint16_t offset_low;
    uint16_t selector;
    uint8_t ist;
    uint8_t type_attr;
    uint16_t offset_mid;
    uint32_t offset_high;
    uint32_t reserved;
} __attribute__((packed));

struct idt_entry idt[256];

void idt_set_gate(uint8_t num, uint64_t handler) {
    idt[num].offset_low = handler & 0xFFFF;
    idt[num].selector = 0x08;  // Code segment
    idt[num].ist = 0;
    idt[num].type_attr = 0x8E;  // Present, DPL=0, 32-bit interrupt
    idt[num].offset_mid = (handler >> 16) & 0xFFFF;
    idt[num].offset_high = (handler >> 32) & 0xFFFFFFFF;
    idt[num].reserved = 0;
}

void idt_load() {
    struct {
        uint16_t limit;
        uint64_t base;
    } __attribute__((packed)) idt_ptr = {sizeof(idt), (uint64_t)idt};
    
    __asm__ volatile ("lidt %0" : : "m"(idt_ptr));
}

// GDT setup
struct gdt_entry {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t base_mid;
    uint8_t access;
    uint8_t flags;
    uint8_t base_high;
} __attribute__((packed));

struct gdt_entry gdt[3];
struct gdt_ptr {
    uint16_t limit;
    uint64_t base;
} __attribute__((packed));

void gdt_set_entry(int num, uint32_t base, uint32_t limit, uint8_t access, uint8_t flags) {
    gdt[num].limit_low = limit & 0xFFFF;
    gdt[num].base_low = base & 0xFFFF;
    gdt[num].base_mid = (base >> 16) & 0xFF;
    gdt[num].access = access;
    gdt[num].flags = (limit >> 16) & 0x0F | (flags << 4);
    gdt[num].base_high = (base >> 24) & 0xFF;
}

void gdt_init() {
    gdt_set_entry(0, 0, 0, 0, 0);  // Null descriptor
    gdt_set_entry(1, 0, 0xFFFFF, 0x9A, 0xA);  // Code segment
    gdt_set_entry(2, 0, 0xFFFFF, 0x92, 0xA);  // Data segment
    
    struct gdt_ptr ptr = {sizeof(gdt), (uint64_t)gdt};
    __asm__ volatile ("lgdt %0" : : "m"(ptr));
    
    // Reload segments
    __asm__ volatile (
        "mov ax, 0x10\n"
        "mov ds, ax\n"
        "mov es, ax\n"
        "mov fs, ax\n"
        "mov gs, ax\n"
        "mov ss, ax\n"
        "jmp 0x08:next\n"
        "next:"
    );
}

// Memory management
typedef struct page {
    uint64_t present : 1;
    uint64_t writable : 1;
    uint64_t user_access : 1;
    uint64_t write_through : 1;
    uint64_t cache_disable : 1;
    uint64_t accessed : 1;
    uint64_t dirty : 1;
    uint64_t huge_page : 1;
    uint64_t global : 1;
    uint64_t available : 3;
    uint64_t frame : 40;
    uint64_t available2 : 11;
    uint64_t nx : 1;
} __attribute__((packed)) page_t;

page_t* page_table = (page_t*)0x100000;

void identity_map(page_t* table) {
    for (uint64_t i = 0; i < 512; i++) {
        table[i].present = 1;
        table[i].writable = 1;
        table[i].frame = i;
    }
}

// Main kernel
void kernel_main() {
    // Initialize GDT
    gdt_init();
    
    // Initialize IDT
    idt_load();
    
    // Map identity pages
    identity_map(page_table);
    
    // Enable paging
    uint64_t cr3 = (uint64_t)page_table;
    __asm__ volatile ("mov cr3, %0" : : "r"(cr3));
    
    // Enable PAE and paging
    uint64_t cr4;
    __asm__ volatile ("mov cr4, %0" : : "r"(cr4));
    cr4 |= 1 << 5;  // PAE
    __asm__ volatile ("mov cr4, %0" : : "r"(cr4));
    
    // Enable long mode (LM) via EFER MSR
    uint64_t efer;
    __asm__ volatile ("rdmsr" : "=a"(efer) : "c"(0xC0000080));
    efer |= 1 << 8;  // LME
    __asm__ volatile ("wrmsr" : : "a"(efer) : "c"(0xC0000080));
    
    // Enable paging
    uint64_t cr0;
    __asm__ volatile ("mov cr0, %0" : "=r"(cr0));
    cr0 |= 1 << 31;  // PG
    __asm__ volatile ("mov cr0, %0" : : "r"(cr0));
    
    print("Hello, Empire OS!\n");
    print("Kernel loaded successfully.\n");
    
    while(1) __asm__ volatile ("hlt");
}
```

---

## 🛠️ Tools

| Tool | Purpose |
|------|---------|
| **QEMU** | Emulator |
| **Bochs** | x86 emulator |
| **GCC** | Cross-compiler |
| **GDB** | Debugger |
| **GRUB** | Bootloader |

---

## 🎯 Next Steps

1. Read "Operating Systems: Three Easy Pieces"
2. Build TutorialOS from scratch
3. Add process scheduling
4. Implement simple FS

**Make it run! 🖥️**
