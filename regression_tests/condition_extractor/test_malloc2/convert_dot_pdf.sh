#!/bin/bash

# dot -Tpdf 7a86ce6b1a05f6e92d2bd7683484013e_create_postdom.txt.dot -o7a86ce6b1a05f6e92d2bd7683484013e_create_postdom.pdf

# dot -Tpdf 7a86ce6b1a05f6e92d2bd7683484013e_create_dom.txt.dot -o7a86ce6b1a05f6e92d2bd7683484013e_create_dom.pdf

# dot -Tpdf 3d19b1a899ca511709064ae8b54dd331_indirect_test_postdom.txt.dot -o3d19b1a899ca511709064ae8b54dd331_indirect_test_postdom.txt.dot.pdf

# dot -Tpdf 3d19b1a899ca511709064ae8b54dd331_indirect_test_dom.txt.dot -o3d19b1a899ca511709064ae8b54dd331_indirect_test_dom.txt.dot.pdf

# dot -Tpdf 3d19b1a899ca511709064ae8b54dd331_create_postdom.txt.dot -o3d19b1a899ca511709064ae8b54dd331_create_postdom.txt.dot.pdf

# dot -Tpdf 3d19b1a899ca511709064ae8b54dd331_create_dom.txt.dot -o3d19b1a899ca511709064ae8b54dd331_create_dom.txt.dot.pdf

# dot -Tpdf ibbgraph_2.dot -oibbgraph_2.dot.pdf
# dot -Tpdf ibbgraph_3.dot -oibbgraph_3.dot.pdf

# for apifun in create first second close third foo indirect_test
# for apifun in create
# do
#     if [ -f "postdom_$apifun.dot" ]; then
#         dot -Tpdf postdom_$apifun.dot -opostdom_$apifun.pdf
#     else 
#         echo "postdom_$apifun.dot does not exist"
#     fi

#     if [ -f "dom_$apifun.dot" ]; then
#         dot -Tpdf dom_$apifun.dot -odom_$apifun.pdf
#     else
#         echo "dom_$apifun.dot does not exist"
#     fi
# done

# dot -Tpdf svfir_initial.dot -osvfir_initial.dot.pdf
dot -Tpdf svfg_final.dot -osvfg_final.dot.pdf