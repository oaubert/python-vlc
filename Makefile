MODULE_NAME=generated/vlc.py
VERSIONED_NAME=generated/2.2/vlc.py

all: $(MODULE_NAME) $(VERSIONED_NAME)

$(MODULE_NAME): generator/generate.py generator/header.py generator/footer.py generator/override.py ../../include/vlc/*.h
	python generator/generate.py ../../include/vlc/*.h -o $@

$(VERSIONED_NAME): generator/generate.py generator/header.py generator/footer.py generator/override.py /usr/include/vlc/*.h
	python generator/generate.py /usr/include/vlc/*.h -o $@

doc: $(MODULE_NAME)
	-epydoc -v -o doc $<

test: $(MODULE_NAME)
	PYTHONPATH=generated python tests/test.py
	PYTHONPATH=generated/2.2 python tests/test.py

test3: $(MODULE_NAME)
	PYTHONPATH=generated python3 tests/test.py
	PYTHONPATH=generated/2.2 python3 tests/test.py

tests: test test3

check: $(MODULE_NAME)
	-pyflakes $<
	-pylint $<

clean:
	-$(RM) $(MODULE_NAME)
