tmv71/%.py: %.ksy
	ksc --target python --outdir tmv71 $<

all: tmv71/memory.py
