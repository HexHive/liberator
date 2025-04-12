CC=/workspaces/libfuzz/llvm-project/build/bin/clang-14

TARGET=driver0

${TARGET}: ${TARGET}.cc
	${CC} -g $< -fsanitize="fuzzer,address" -o $@

run: ${TARGET}
	COV_PLATEAU_TIMEOUT=15 timeout -k 10s 2m ./driver0 -ignore_crashes=1 -ignore_timeouts=1 -ignore_ooms=1 -detect_leaks=0

clean:
	rm -f ${TARGET} crash-* leak-*