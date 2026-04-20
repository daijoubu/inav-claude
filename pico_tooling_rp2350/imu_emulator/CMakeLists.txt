cmake_minimum_required(VERSION 3.13)

# Pull in Pico SDK
set(PICO_SDK_PATH "${CMAKE_CURRENT_LIST_DIR}/../pico-sdk")
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(mpu6000_emu C CXX ASM)
set(CMAKE_C_STANDARD 11)

pico_sdk_init()

add_executable(mpu6000_emu
    mpu6000_emu.c
)

target_link_libraries(mpu6000_emu
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_irq
    hardware_timer
)

# Enable USB stdio for command interface, disable UART stdio
pico_enable_stdio_usb(mpu6000_emu 1)
pico_enable_stdio_uart(mpu6000_emu 0)

# Generate UF2 for drag-and-drop flashing
pico_add_extra_outputs(mpu6000_emu)
