

test: test.cc
	$(CXX) -g -std=c++11 -I/library/work/include -fsanitize=address \
		$< -Wl,--whole-archive /library/work/lib/libcjson.a -Wl,--no-whole-archive \
		-lz -ljpeg -Wl,-Bstatic -llzma -Wl,-Bdynamic -lstdc++ -o $@

clean:
	rm -Rf test