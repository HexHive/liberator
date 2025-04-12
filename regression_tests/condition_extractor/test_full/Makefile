# export CC = wllvm
# export CXX = wllvm++
export CC = clang
export CXX = clang++
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
FUNCTION = set_data
INTERFACE = $(PWD)/apis_clang.json
EXTR_INC_FUNC = /workspaces/libfuzz/tool/misc/extract_included_functions.py
CACHE_FOLDER = $(shell pwd)
DRIVER_GENERATION = /workspaces/libfuzz/tool/main.py
GENERATOR_CONF = /workspaces/libfuzz/regression_tests/condition_extractor/test_full/generator.toml
DATA_LAYOUT = datalayout.txt

$(TARGET).o: $(TARGET).c
	rm -f apis_llvm.log apis_clang.json 
	$(CXX) -O0 -g -c $<
#	$(CC) -O0 -g -c $<

$(TARGET).o.bc: $(TARGET).o
	$(EXTRACT_BC) -b $<

$(TARGET).o.ll: $(TARGET).o.bc
	$(LLVM_DIS) $<

run: $(TARGET).o.bc $(TARGET).o.ll
	@echo "Running condition_extractor"
#	$(WPA) -steens --dump-icfg  ./$(TARGET).o.bc
	$(EXTR_INC_FUNC) -i $(PWD) -e "$(PWD)/exported_functions.txt" -t "$(PWD)/incomplete_types.txt" -a $(INTERFACE)
	$(EXTRACTOR) $< -interface $(INTERFACE) -t json -v v0  -output $(TARGET).json -data_layout $(DATA_LAYOUT)
#	$(EXTRACTOR) $< -function $(FUNCTION) -t json -output $(TARGET).json -v v1 -dom  -print_dom
# 	$(EXTRACTOR) $< -function $(FUNCTION) -t json -output $(TARGET).json -v v0 -do_indirect_jumps
#	$(EXTRACTOR) $< -function $(FUNCTION) -t txt -output $(TARGET).txt -v v0 -do_indirect_jumps
# 	$(WPA) -ander -svfg --dump-vfg  ./$(TARGET).o.bc
#	$(WPA) -ander -dump-pag ./$(TARGET).o.bc
# 	convert only if you --print_dom
# 	./convert_dot_pdf.sh

gen: apis_llvm.json apis_clang.json coerce.log exported_functions.txt incomplete_types.txt $(TARGET).json
	@echo "Generating drivers"
	$(DRIVER_GENERATION) --config $(GENERATOR_CONF) 

driver0: workdir/drivers/driver0.cc library.a
	clang++ -g -I. -fsanitize=address,fuzzer $? -o driver0

clean:
	rm -f $(TARGET).o $(TARGET).o.bc .$(TARGET).o.bc $(TARGET).o.svf.bc $(TARGET).o.ll apis_llvm.log apis_llvm.json *.pdf dom*.dot postdom*.dot dom*.txt postdom*.txt
