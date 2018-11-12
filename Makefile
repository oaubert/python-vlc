GENERATE:=python3 generator/generate.py
DEV_INCLUDE_DIR=../../include/vlc
INSTALLED_INCLUDE_DIR=/usr/include/vlc

DEV_PATH=generated/dev
VERSIONED_PATH=generated/3.0

MODULE_NAME=$(DEV_PATH)/vlc.py
VERSIONED_NAME=$(VERSIONED_PATH)/vlc.py

DEV_INCLUDES=$(wildcard $(DEV_INCLUDE_DIR)/*.h)
INSTALLED_INCLUDES=$(wildcard $(INSTALLED_INCLUDE_DIR)/*.h)

ifneq ($(DEV_INCLUDES),)
TARGETS+=dev
endif
ifneq ($(INSTALLED_INCLUDES),)
TARGETS+=installed dist
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

dist: $(VERSIONED_NAME)
	$(GENERATE) -p $<

deb: dist
	cd $(VERSIONED_PATH) ; python setup.py --command-packages=stdeb.command sdist_dsc --with-python2=true --with-python3=true --copyright-file=COPYING bdist_deb

$(MODULE_NAME): generator/generate.py generator/templates/header.py generator/templates/footer.py generator/templates/override.py $(DEV_INCLUDES)
	-mkdir -p $(DEV_PATH)
	$(GENERATE) $(DEV_INCLUDES) -o $@

$(VERSIONED_NAME): generator/generate.py generator/templates/header.py generator/templates/footer.py generator/templates/override.py $(INSTALLED_INCLUDES)
	-mkdir -p $(VERSIONED_PATH)
	$(GENERATE) $(INSTALLED_INCLUDES) -o $@

doc: $(MODULE_NAME)
	-epydoc -v -o doc $<

test: $(MODULE_NAME)
	PYTHONPATH=$(DEV_PATH) python tests/test.py
	PYTHONPATH=$(VERSIONED_PATH) python tests/test.py

test3: $(MODULE_NAME)
	PYTHONPATH=$(DEV_PATH) python3 tests/test.py
	PYTHONPATH=$(VERSIONED_PATH) python3 tests/test.py

publish: $(VERSIONED_NAME)
	cd $(VERSIONED_PATH); python3 setup.py bdist_wheel sdist && twine upload dist/*

tests: test test3

check: $(MODULE_NAME)
	-pyflakes $<
	-pylint $<

clean:
	-$(RM) -r $(DEV_PATH)
	-$(RM) -r $(VERSIONED_PATH)
