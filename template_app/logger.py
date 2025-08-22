# This file uses PyQt6
import logging
import sys

# Create a custom handler that writes to stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)

# Create a file handler for persistent logs
file_handler = logging.FileHandler('supercut.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(console_formatter)

# Configure the root logger
logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])

logger = logging.getLogger('SuperCut') 