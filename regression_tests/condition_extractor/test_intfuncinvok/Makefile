
export CC = wllvm
export CXX = wllvm++
export LLVM_COMPILER = clang
export LLVM_COMPILER_PATH=${LLVM_DIR}/bin
export LIBFUZZ_LOG_PATH=$(shell pwd)


TARGET = library
EXTRACTOR = /workspaces/libfuzz/condition_extractor/bin/extractor
LLVM_DIS = ${LLVM_DIR}/bin/llvm-dis
WPA = /root/SVF/Release-build/bin/wpa
EXTRACT_BC = extract-bc
FUNCTION1 = api1
FUNCTION2 = api2

$(TARGET).o: $(TARGET).c
	$(CC) -O0 -g -mllvm -get-api-pass -c $<

$(TARGET).o.bc: $(TARGET).o
	$(EXTRACT_BC) -b $<

$(TARGET).o.ll: $(TARGET).o.bc
	$(LLVM_DIS) $<

run: $(TARGET).o.bc $(TARGET).o.ll
	@echo "Running condition_extractor"
	$(EXTRACTOR) $< -function $(FUNCTION1) -t json -output $(FUNCTION1).json -v v1
#	$(EXTRACTOR) $< -function $(FUNCTION2) -t json -output $(FUNCTION2).json -v v1
#	$(WPA) -steens -svfg --dump-vfg  ./$(TARGET).o.bc
#	$(WPA) -ander -svfg --dump-vfg  ./$(TARGET).o.bc

clean:
	rm -f $(TARGET).o $(TARGET).o.bc .$(TARGET).o.bc $(TARGET).o.svf.bc $(TARGET).o.ll 