There are searchable indexes to the datasheets and other documentation about each chip:

rp2350/ (pico2)
stm32f405/ (F405)
stm32f722/ (F722)
stm32f745/ (F745)
stm32f765/ (F765/F767/F768/F769)
stm32h7/ (H7)

There is a search script for each chip within those directories. Use the search script when you need to know about pin assignments, alternate functions (AF), or any other information about the processors.

The search script handles three types of queries:
- Pin name (e.g. PA5, PB3)  → shows all alternate functions for that pin
- Signal name (e.g. SPI1_SCK, USART1_TX) → shows which pins support that signal
- General keyword (e.g. DMA, timer) → searches the PDF index and extracts relevant pages

