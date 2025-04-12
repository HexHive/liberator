
test: test.cc
	$(CXX) -g -std=c++11 -I${HOME}/library/work/include \
		$< -Wl,--whole-archive ${HOME}/library/work/lib/libcjson.a -Wl,--no-whole-archive \
		-fsanitize=address \
		-lz -ljpeg -Wl,-Bstatic -llzma -Wl,-Bdynamic -lstdc++ -o $@

clean:
	rm -Rf test