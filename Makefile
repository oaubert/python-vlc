MODULE_NAME=generated/vlc.py

all: $(MODULE_NAME)

$(MODULE_NAME): generate.py header.py footer.py override.py ../../include/vlc/*.h
	python generate.py ../../include/vlc/*.h -o $@

doc: $(MODULE_NAME)
	-epydoc -v -o doc $<

test: $(MODULE_NAME)
	PYTHONPATH=generated python test.py

test3: $(MODULE_NAME)
	PYTHONPATH=generated python3 test.py

tests: test test3

check: $(MODULE_NAME)
	-pyflakes $<
	-pylint $<

clean:
	-$(RM) $(MODULE_NAME)
