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
FUNCTION = loop_indirect
INTERFACE = $(PWD)/apis_clang.json
EXTR_INC_FUNC = /workspaces/libfuzz/tool/misc/extract_included_functions.py
CACHE_FOLDER = $(shell pwd)

$(TARGET).o: $(TARGET).c
	rm -f apis_llvm.log apis_clang.json 
	$(CC) -O0 -g -mllvm -get-api-pass -c $<

$(TARGET).o.bc: $(TARGET).o
	$(EXTRACT_BC) -b $<

$(TARGET).o.ll: $(TARGET).o.bc
	$(LLVM_DIS) $<

run: $(TARGET).o.bc $(TARGET).o.ll
	@echo "Running condition_extractor"
#	$(WPA) -steens --dump-icfg  ./$(TARGET).o.bc
#	$(EXTR_INC_FUNC) -i $(PWD) -e "$(PWD)/exported_functions.txt" -t "$(PWD)/incomplete_types.txt" -a $(INTERFACE)
	$(EXTRACTOR) $< -function $(FUNCTION) -t json -output $(TARGET).json -v v0 -do_indirect_jumps
#	$(EXTRACTOR) $< -function $(FUNCTION) -t txt -output $(TARGET).txt -v v0 -do_indirect_jumps
#	$(WPA) -ander -svfg --dump-vfg  ./$(TARGET).o.bc
#	$(WPA) -ander -dump-pag ./$(TARGET).o.bc
#	convert only if you --print_dom
#	./convert_dot_pdf.sh

clean:
	rm -f $(TARGET).o $(TARGET).o.bc .$(TARGET).o.bc $(TARGET).o.svf.bc $(TARGET).o.ll apis_llvm.log apis_llvm.json *.pdf dom*.dot postdom*.dot dom*.txt postdom*.txt
