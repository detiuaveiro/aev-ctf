# Build the handout binary locally (also needed by solve.py to resolve win()).
.PHONY: build clean
build: build/vuln

build/vuln: src/vuln.c
	@mkdir -p build
	gcc -fno-stack-protector -no-pie -O0 -w -o build/vuln src/vuln.c

clean:
	rm -rf build
