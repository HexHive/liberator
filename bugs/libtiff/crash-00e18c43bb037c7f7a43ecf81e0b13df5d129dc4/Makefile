

test: test.cc
	$(CXX) -g -std=c++11 -I${HOME}/library/work/include -fsanitize=address \
		$< -Wl,--whole-archive ${HOME}/library/work/lib/libtiff_cluster.a -Wl,--no-whole-archive \
		-lz -ljpeg -Wl,-Bstatic -llzma -Wl,-Bdynamic -lstdc++ -o $@

clean:
	rm -Rf test