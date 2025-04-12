#!/bin/bash

for d in `find ./workdir_*_*/*/results/ -name "iter_1"`; do
        # echo $d
        x=${d::-1}"5"
        # echo $x
        mv $d $x
done