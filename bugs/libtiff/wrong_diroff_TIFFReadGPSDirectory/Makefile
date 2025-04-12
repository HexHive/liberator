CC=$(LLVM_DIR)/bin/clang

all: poc.c
	$(CC) $? -gdwarf-4 -fsanitize=address -I/${TARGET}/work/include \
        -Wl,--whole-archive ${TARGET}/work/lib/libtiff_cluster.a ${TARGET}/work/lib/libtiffxx_cluster.a -Wl,--no-whole-archive \
        -lz -ljpeg -Wl,-Bstatic -llzma -Wl,-Bdynamic -lstdc++ -o poc.out

crash: all
	./poc.out poc.tiff

clean:
	rm poc.out || true
