#!/usr/bin/env python3
"""Demonstrate Linux ru_maxrss retention across fork/exec on this host.
This is a diagnostic of OS accounting, not evidence of a particular evaluator implementation.
"""
import os,subprocess,sys
from pathlib import Path
here=Path(__file__).resolve().parent
prog=here/'measure_exec_memory'
subprocess.run(['cc','-O2',str(here/'measure_exec_memory.c'),'-o',str(prog)],check=True)
print('Before allocating parent memory:')
subprocess.run([str(prog)],check=True)
block=bytearray(70*1024*1024)
for pos in range(0,len(block),4096):block[pos]=1
print('After allocating 70 MiB in the launching Python process:')
subprocess.run([str(prog)],check=True)
