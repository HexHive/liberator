export CC = wllvm
export CXX = wllvm++
export LLVM_COMPILER = clang
export LLVM_COMPILER_PATH=${LLVM_DIR}/bin
export LIBFUZZ_LOG_PATH=$(shell pwd)

TARGET = library
EXTRACTOR = /workspaces/libfuzz/condition_extractor/bin/extractor
FUNCTION = api1
LLVM_DIS = ${LLVM_DIR}/bin/llvm-dis
WPA = /root/SVF/Release-build/bin/wpa
EXTRACT_BC = extract-bc
FUNCTION = api1

$(TARGET).o: $(TARGET).c
	$(CC) -O0 -g -mllvm -get-api-pass -c $<

$(TARGET).o.bc: $(TARGET).o
	$(EXTRACT_BC) -b $<

$(TARGET).o.ll: $(TARGET).o.bc
	$(LLVM_DIS) $<

run: $(TARGET).o.bc $(TARGET).o.ll
	@echo "Running condition_extractor"
	$(EXTRACTOR) $< -function $(FUNCTION) -t json -output $(TARGET).json -v v2 -debug_condition "(.6, none"
	$(WPA) -steens -svfg --dump-vfg  ./$(TARGET).o.bc
#	$(WPA) -ander -svfg --dump-vfg  ./$(TARGET).o.bc

clean:
	rm -f $(TARGET).o $(TARGET).o.bc .$(TARGET).o.bc $(TARGET).o.svf.bc $(TARGET).o.ll apis_llvm.json