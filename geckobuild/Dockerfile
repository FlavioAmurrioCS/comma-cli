FROM debian:bullseye

# curl https://sh.rustup.rs -sSf | sh

RUN : && \
    apt update && \
    apt install -y curl unzip gcc-arm-linux-gnueabihf libc6-armhf-cross libc6-dev-armhf-cross build-essential&& \
    curl https://sh.rustup.rs -sSf -o /tmp/foo.sh && \
    sh /tmp/foo.sh -y
RUN . /root/.cargo/env && \
    rustup target install armv7-unknown-linux-gnueabihf && \
    :
WORKDIR /tmp/mozilla




# apt update
# apt install -y curl gcc-arm-linux-gnueabihf libc6-armhf-cross libc6-dev-armhf-cross
# curl https://sh.rustup.rs -sSf -o /tmp/foo.sh
# sh /tmp/foo.sh -y
# source $HOME/.cargo/env
# rustup target install armv7-unknown-linux-gnueabihf
# cd testing/geckodriver

# cargo build --release --target armv7-unknown-linux-gnueabihf
