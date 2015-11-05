MODULE_NAME=generated/vlc.py

all: $(MODULE_NAME)

$(MODULE_NAME): generator/generate.py generator/header.py generator/footer.py generator/override.py ../../include/vlc/*.h
	python generator/generate.py ../../include/vlc/*.h -o $@

doc: $(MODULE_NAME)
	-epydoc -v -o doc $<

test: $(MODULE_NAME)
	PYTHONPATH=generated python tests/test.py

test3: $(MODULE_NAME)
	PYTHONPATH=generated python3 tests/test.py

tests: test test3

check: $(MODULE_NAME)
	-pyflakes $<
	-pylint $<

clean:
	-$(RM) $(MODULE_NAME)
