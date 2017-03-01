DEV_INCLUDE_DIR=../../include/vlc
INSTALLED_INCLUDE_DIR=/usr/include/vlc
MODULE_NAME=generated/vlc.py
VERSIONED_NAME=generated/2.2/vlc.py

DEV_INCLUDES=$(wildcard $(DEV_INCLUDE_DIR)/*.h)
INSTALLED_INCLUDES=$(wildcard $(INSTALLED_INCLUDE_DIR)/*.h)

ifneq ($(DEV_INCLUDES),)
TARGETS+=dev
endif
ifneq ($(INSTALLED_INCLUDES),)
TARGETS+=installed
endif
ifeq ($(TARGETS),)
TARGETS=missing
endif

all: $(TARGETS)

missing:
	@echo "Cannot find include files either from a source tree in $(DEV_INCLUDE_DIR) or from installed includes in $(INSTALLED_INCLUDE_DIR)."
	exit 0

.ONESHELL:
dev: $(MODULE_NAME)
	@if [ ! -d $(DEV_INCLUDE_DIR) ]; then echo "The bindings directory must be placed in a VLC source tree as vlc/bindings/python to generate the dev version of the bindings. If you want to generate against installed include files, use the 'installed' target." ; exit 1 ; fi

installed: $(VERSIONED_NAME)
	@if [ ! -d $(INSTALLED_INCLUDE_DIR) ]; then echo "Cannot find the necessary VLC include files in $(INSTALLED_INCLUDE_DIR). Make sure a full VLC install is present on the system." ; exit 1 ; fi

$(MODULE_NAME): generator/generate.py generator/header.py generator/footer.py generator/override.py $(DEV_INCLUDES)
	python generator/generate.py $(DEV_INCLUDES) -o $@

$(VERSIONED_NAME): generator/generate.py generator/header.py generator/footer.py generator/override.py $(INSTALLED_INCLUDES)
	python generator/generate.py $(INSTALLED_INCLUDES) -o $@

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
