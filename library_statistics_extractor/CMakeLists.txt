cmake_minimum_required(VERSION 3.4.3)
project("Library Statistics Extractor")
if (DEFINED LLVM_DIR)
        set(ENV{LLVM_DIR} "${LLVM_DIR}")
    endif()
    if (DEFINED ENV{LLVM_DIR})
        # We need to match the build environment for LLVM:
        # In particular, we need C++11 and the -fno-rtti flag
        set(CMAKE_CXX_STANDARD 14)
	if(CMAKE_BUILD_TYPE MATCHES "Debug")
		set(CMAKE_CXX_FLAGS "-fPIC -std=gnu++14 -O0 -fno-rtti -Wno-deprecated -Wfatal-errors")
	else()
		set(CMAKE_CXX_FLAGS "-fPIC -std=gnu++14 -O0 -fno-rtti -Wno-deprecated -Wfatal-errors")
	endif()
	set(CMAKE_C_FLAGS "-fPIC")

find_package(LLVM REQUIRED CONFIG)
    
    list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")
    include(AddLLVM)

    add_definitions(${LLVM_DEFINITIONS})
    include_directories(${LLVM_INCLUDE_DIRS})

else()
    message(FATAL_ERROR "\
WARNING: The LLVM_DIR var was not set (required for an out-of-source build)!\n\
Please set this to environment variable to point to the LLVM build directory\
(e.g. on linux: export LLVM_DIR=/path/to/llvm/build/dir)")
endif()

if (EXISTS "${SVF_DIR}")
else()
    set(SVF_DIR $ENV{SVF_DIR})
    if(EXISTS "${SVF_DIR}")
    else()
    message(FATAL_ERROR "\
WARNING: The SVF_DIR var was not set (required for an out-of-source build)!\n\
Please set this to environment variable to point to the SVF_DIR directory or set this variable to cmake configuration\n
(e.g. on linux: export SVF_DIR=/path/to/SVF/dir) \n or \n \n(make the project via: cmake -DSVF_DIR=your_path_to_SVF) ")
    endif()
endif()

if(CMAKE_BUILD_TYPE MATCHES "Debug")
    MESSAGE (STATUS "building SVF in debug mode")
    if (EXISTS "${SVF_DIR}/Debug-build")
        set(SVF_BIN "${SVF_DIR}/Debug-build")
    else()
        set(SVF_BIN "${SVF_DIR}/Release-build")
    endif()
else()
    MESSAGE (STATUS "building SVF in release mode")
    set(SVF_BIN "${SVF_DIR}/Release-build")
endif()
set(SVF_HEADER "${SVF_DIR}/svf/include")
set(SVF_LLVM_HEADER "${SVF_DIR}/svf-llvm/include")
set(SVF_LIB "${SVF_BIN}/svf-llvm/libSvfLLVM.a")
set(SVF_BIN_HEADER "${SVF_BIN}/include")
include_directories(${SVF_HEADER}
                    ${SVF_LLVM_HEADER}
                    ${SVF_BIN_HEADER})

#set z3 env
if (DEFINED Z3_DIR)
    set(ENV{Z3_DIR} "${Z3_DIR}")
endif()
if(CMAKE_BUILD_TYPE MATCHES "Debug")
    if(EXISTS "${Z3_DIR}/src")
        find_package(Z3 REQUIRED CONFIG)
        include_directories(${Z3_CXX_INCLUDE_DIRS})
    else()
        find_library(Z3_LIBRARIES NAMES libz3.a libz3.so
                HINTS $ENV{Z3_DIR}
                PATH_SUFFIXES bin)
        find_path(Z3_INCLUDES NAMES z3++.h
                HINTS $ENV{Z3_DIR}
                PATH_SUFFIXES include z3)
        if(NOT Z3_LIBRARIES OR NOT Z3_INCLUDES)
            message(FATAL_ERROR "Z3 not found!")
        endif()
        include_directories(${Z3_INCLUDES})
        LINK_DIRECTORIES(${Z3_DIR}/bin)
    endif()
else()
    find_library(Z3_LIBRARIES NAMES libz3.a libz3.so
            HINTS $ENV{Z3_DIR}
            PATH_SUFFIXES bin)
    find_path(Z3_INCLUDES NAMES z3++.h
            HINTS $ENV{Z3_DIR}
            PATH_SUFFIXES include z3)
    if(NOT Z3_LIBRARIES OR NOT Z3_INCLUDES)
        message(FATAL_ERROR "Z3 not found!")
    endif()
    include_directories(${Z3_INCLUDES})
    LINK_DIRECTORIES(${Z3_DIR}/bin)
endif()

add_subdirectory(src)
