# syntax=docker/dockerfile:1

FROM ubuntu:20.04 AS libfuzzpp_dev_image

RUN --mount=type=cache,target=/var/cache/apt apt-get -q update && \
    DEBIAN_FRONTEND="noninteractive" \
    apt-get -y install --no-install-suggests --no-install-recommends \
    sudo make ninja-build texinfo bison zsh ccache autoconf libtool \
    zlib1g-dev liblzma-dev libjpeg-turbo8-dev automake cmake nasm \
    build-essential git openssh-client python3 python3-dev \
    python3-setuptools python-is-python3 python3-venv python3-pip \
    libtool libtool-bin libglib2.0-dev wget vim jupp nano \
    bash-completion less apt-utils apt-transport-https curl  \
    ca-certificates gnupg dialog libpixman-1-dev gnuplot-nox \
    nodejs npm graphviz libtinfo-dev libz-dev zip unzip libclang-12-dev \
    tmux tree gdb jq bc cloc ccache lsb-release lsof cargo \
    && rm -rf /var/lib/apt/lists/*

# Clang dependencies
RUN --mount=type=cache,target=/var/cache/apt apt-get update && apt-get full-upgrade -y && \
    DEBIAN_FRONTEND="noninteractive" \
    apt-get -y install --no-install-suggests --no-install-recommends \
        gcc g++ libncurses5


ARG USERNAME=libfuzz
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s/bin/zsh $USERNAME \
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
        && chown -R root /usr/bin/sudo \
    && chmod 4755 /usr/bin/sudo \
    && chown -R $USERNAME /home/$USERNAME

ENV HOME=/home/${USERNAME}
USER ${USERNAME}
WORKDIR ${HOME}
ENV CCACHE_DIR=${HOME}/.ccache
RUN echo "export PATH=\$PATH:${HOME}/.local/bin" >> ~/.bashrc
RUN echo "export PATH=\$PATH:${HOME}/.local/bin" >> ~/.zshrc
RUN --mount=type=cache,target=${CCACHE_DIR} mkdir -p ${CCACHE_DIR} && sudo -E chown -R ${USERNAME}:${USERNAME} ${CCACHE_DIR}

RUN pip3 install ipython
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN $HOME/.cargo/bin/cargo install casr

ENV LIBFUZZ /workspaces/libfuzz

RUN --mount=type=cache,target=/var/cache/apt sudo apt-get update && sudo apt-get full-upgrade -y && \
    DEBIAN_FRONTEND="noninteractive" \
    sudo apt-get -y install --no-install-suggests --no-install-recommends \
        gcc g++ libncurses5  clang-12 llvm-12-dev

# gef
RUN echo "export LC_CTYPE=C.UTF-8" >> ~/.bashrc
RUN echo "export LC_CTYPE=C.UTF-8" >> ~/.zshrc
RUN bash -c "$(curl -fsSL https://gef.blah.cat/sh)"

# SVF

RUN --mount=type=cache,target=${HOME}/.ccache/ git clone https://github.com/SVF-tools/SVF.git && \
    cd SVF && \
    git checkout f889cfbf7a4694183abbb3417f81887a44acab29 && \
    sed -i 's/jobs=4/jobs=/g' build.sh && \
    ./build.sh
RUN cd SVF && ./setup.sh

COPY ./requirements.txt ${HOME}/python/requirements.txt
RUN cd ${HOME}/python && python3 -m pip install -r requirements.txt

# ------------------------------------------------------------------------------------------------------------------
# TARGET FOR LIBRARY DEBUG
FROM libfuzzpp_dev_image AS libfuzzpp_debug

ENV TOOLS_DIR ${HOME}
ARG target_name=simple_connection

ENV TARGET_NAME ${target_name}

COPY --link ./llvm-project/build ${HOME}/LLVM/
ENV LLVM_DIR ${HOME}/LLVM
# ENV LLVM_DIR ${LIBFUZZ}/llvm-project/build
ENV TARGET ${HOME}/library
ENV DRIVER_FOLDER ${LIBFUZZ}/workdir/${TARGET_NAME}/drivers
ENV DRIVER "*"

RUN mkdir -p ${HOME}/${TARGET_NAME}
WORKDIR ${HOME}/${TARGET_NAME}
COPY --chown=${USERNAME}:${USERNAME}  ./targets/${TARGET_NAME}/preinstall.sh ${HOME}/${TARGET_NAME}
RUN sudo ./preinstall.sh
COPY --chown=${USERNAME}:${USERNAME}  ./targets/${TARGET_NAME}/fetch.sh ${HOME}/${TARGET_NAME}
RUN ./fetch.sh
COPY --chown=${USERNAME}:${USERNAME}  ./targets/${TARGET_NAME}/build_library.sh ${HOME}/${TARGET_NAME}
RUN sed -i 's/-g /-gdwarf-4 /g' ./build_library.sh; 
RUN sed -i 's/-g\"/-gdwarf-4\"/g' ./build_library.sh
RUN ./build_library.sh
COPY --chown=${USERNAME}:${USERNAME}  ./targets/${TARGET_NAME}/compile_driver.sh ${HOME}/${TARGET_NAME}
RUN sed -i 's/-g /-gdwarf-4 /g' ./compile_driver.sh
RUN bash -c "$(curl -fsSL https://gef.blah.cat/sh)"
RUN echo "PROMPT=\"Debug \"\$PROMPT" >> ~/.zshrc

WORKDIR ${LIBFUZZ}

# ------------------------------------------------------------------------------------------------------------------
# TARGET FOR LIBRARY ANALYSIS
FROM libfuzzpp_dev_image AS libfuzzpp_analysis

ENV TOOLS_DIR ${HOME}

RUN mkdir -p ${TOOLS_DIR}/condition_extractor/
RUN mkdir -p ${TOOLS_DIR}/tool/misc/
RUN sudo apt-get install zlib1g-dev unzip cmake gcc g++ libtinfo5 nodejs
COPY --chown=${USERNAME}:${USERNAME} ./condition_extractor ${TOOLS_DIR}/condition_extractor/
COPY --chown=${USERNAME}:${USERNAME} ./tool/misc/extract_included_functions.py ${TOOLS_DIR}/tool/misc/
# ENV SVF_DIR /home/libfuzz/SVF
# ENV LLVM_DIR /home/libfuzz/SVF
RUN cd ${TOOLS_DIR}/condition_extractor && rm -Rf CMakeCache.txt CMakeFiles && ./bootstrap.sh && make -j

# NOTE: start_analysis.sh finds out its configuration automatically

COPY LLVM/update-alternatives-clang.sh .
RUN sudo ./update-alternatives-clang.sh 12 200
ENV PATH $PATH:${HOME}/.local/bin
RUN echo $PATH
CMD ${LIBFUZZ}/targets/start_analysis.sh

# ------------------------------------------------------------------------------------------------------------------
# TARGET FOR DRIVER GENERATION
FROM libfuzzpp_dev_image AS libfuzzpp_drivergeneration

ARG target_name=simple_connection

# NOTE: start_generate_drivers.sh finds out its configuration automatically
WORKDIR ${LIBFUZZ}/targets/${TARGET_NAME}
CMD ${LIBFUZZ}/targets/start_generate_drivers.sh

# ------------------------------------------------------------------------------------------------------------------
# TARGET FOR FUZZING SESSION
FROM libfuzzpp_dev_image AS libfuzzpp_fuzzing

ARG target_name=simple_connection
# ARG timeout=10m
# ARG driver=*.cc

# COPY LLVM/update-alternatives-clang.sh .
# RUN sudo ./update-alternatives-clang.sh 12 200
# ENV LLVM_DIR /usr
COPY --link ./llvm-project/build ${HOME}/LLVM/
ENV LLVM_DIR ${HOME}/LLVM

ENV TARGET_NAME ${target_name}
ENV TARGET ${HOME}/library
ENV DRIVER_FOLDER ${LIBFUZZ}/workdir/${TARGET_NAME}/drivers

# I want to install the library at building time, so later I only need to build
# the drivers
WORKDIR ${LIBFUZZ}/targets/${TARGET_NAME}
COPY --chown=${USERNAME}:${USERNAME}  ./targets/${TARGET_NAME}/preinstall.sh ${LIBFUZZ}/targets/${TARGET_NAME}
RUN sudo ./preinstall.sh
COPY --chown=${USERNAME}:${USERNAME}  ./targets/${TARGET_NAME}/fetch.sh ${LIBFUZZ}/targets/${TARGET_NAME}
RUN ./fetch.sh
COPY --chown=${USERNAME}:${USERNAME}  ./targets/${TARGET_NAME}/build_library.sh ${LIBFUZZ}/targets/${TARGET_NAME}
RUN ./build_library.sh

# NOTE: start_fuzz_driver.sh finds out its configuration automatically
WORKDIR /tmp
CMD ${LIBFUZZ}/targets/start_fuzz_driver.sh

# ------------------------------------------------------------------------------------------------------------------
# TARGET FOR COVERAGE
FROM libfuzzpp_fuzzing AS libfuzzpp_coverage

WORKDIR ${LIBFUZZ}
ENV PROJECT_COVERAGE ${LIBFUZZ}/workdir/${TARGET_NAME}/coverage_data
ENV DRIVER_FOLDER ${LIBFUZZ}/workdir/${TARGET_NAME}/drivers
ENV CORPUS_FOLDER ${LIBFUZZ}/workdir/${TARGET_NAME}/corpus_new
CMD ${LIBFUZZ}/targets/start_coverage.sh

# ------------------------------------------------------------------------------------------------------------------
# TARGET FOR CRASH CLUSTERING
FROM libfuzzpp_fuzzing AS libfuzzpp_crash_cluster

WORKDIR ${LIBFUZZ}
ENV TARGET_WORKDIR ${LIBFUZZ}/workdir/${TARGET_NAME}
CMD ${LIBFUZZ}/targets/start_clustering.sh

# ------------------------------------------------------------------------------------------------------------------
# TARGET FOR FUZZING CAMPAIGNS
FROM libfuzzpp_dev_image AS libfuzzpp_fuzzing_campaigns
COPY LLVM/update-alternatives-clang.sh .
RUN sudo ./update-alternatives-clang.sh 12 200
WORKDIR ${LIBFUZZ}

# ------------------------------------------------------------------------------------------------------------------
# TARGET FOR DYNAMIC DRIVER CREATION
FROM libfuzzpp_fuzzing AS libfuzzpp_dyndrvgen
ENV DRIVER_FOLDER ""
WORKDIR ${LIBFUZZ}
COPY LLVM/update-alternatives-clang.sh .
RUN sudo ./update-alternatives-clang.sh 12 200
CMD ${LIBFUZZ}/targets/start_dyndrvcreation.sh
