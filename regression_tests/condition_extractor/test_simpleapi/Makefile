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
# FUNCTION = needs_array
# FUNCTION = needs_array_1
# FUNCTION = do_casting
# FUNCTION = indirect_test
# FUNCTION = first
# FUNCTION = foo
FUNCTION = create
INTERFACE = $(PWD)/trueapis_clang.json
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
#	$(EXTRACTOR) $< -interface $(INTERFACE) -t json -output $(TARGET).json -v v0 -dom
#	$(EXTRACTOR) $< -function $(FUNCTION) -t json -output $(TARGET).json -v v1 -dom -print_dom -cache_folder $(CACHE_FOLDER)
#	$(EXTRACTOR) $< -function $(FUNCTION) -t json -output $(TARGET).json -v v1 -dom  -print_dom
	$(EXTRACTOR) $< -function $(FUNCTION) -t json -output $(TARGET).json -v v0 -do_indirect_jumps
#	$(EXTRACTOR) $< -function $(FUNCTION) -t txt -output $(TARGET).txt -v v0 -do_indirect_jumps
# 	$(WPA) -ander -svfg --dump-vfg  ./$(TARGET).o.bc
#	$(WPA) -ander -dump-pag ./$(TARGET).o.bc
# 	convert only if you --print_dom
# 	./convert_dot_pdf.sh

clean:
	rm -f $(TARGET).o $(TARGET).o.bc .$(TARGET).o.bc $(TARGET).o.svf.bc $(TARGET).o.ll apis_llvm.log apis_llvm.json *.pdf dom*.dot postdom*.dot dom*.txt postdom*.txt
