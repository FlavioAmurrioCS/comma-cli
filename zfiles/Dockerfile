FROM ubuntu:jammy
USER root

ENV LANG=C.UTF-8
ENV TERM=xterm-256color
ENV COLORTERM=truecolor

ARG DEVENV_GROUP_ID=20
ARG DEVENV_USER_ID=501
ARG DEVENV_USERNAME=flavio

SHELL ["/bin/bash", "-c"]

# hadolint ignore=DL3008,DL3009,DL3013,SC2086
RUN : \
    && echo "================================================ CREATE USER ===============================================" \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y sudo curl wget git bash apt-utils gpg-agent zip unzip \
    && groupadd --force --gid "${DEVENV_GROUP_ID}" domain_users \
    && useradd -ms /bin/bash --no-log-init "${DEVENV_USERNAME}" "--uid=${DEVENV_USER_ID}" "--gid=${DEVENV_GROUP_ID}" \
    && chpasswd < <(echo "${DEVENV_USERNAME}:docker") \
    && usermod -aG sudo "${DEVENV_USERNAME}" \
    && :

RUN : \
    && echo "============================================ ADD USER TO SUDOERS ===========================================" \
    && echo "${DEVENV_USERNAME} ALL=(ALL) NOPASSWD: ALL" >>/etc/sudoers \
    && echo "${DEVENV_USERNAME} ALL=(ALL) NOPASSWD: ALL" >>/etc/sudoers \
    && echo "Defaults:${DEVENV_USERNAME} "'!requiretty' >>/etc/sudoers \
    && echo "Defaults:${DEVENV_USERNAME} "'!requiretty' >>/etc/sudoers \
    && :

# hadolint ignore=DL3008,DL3009,SC2016
RUN : \
    && echo "============================================== INSTALL COMMON TOOLS ========================================" \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y software-properties-common neovim krb5-user openssh-server openssh-client \
    && echo -e '#!/usr/bin/env sh\nsudo service ssh start\nsudo service docker start\n"${@}"' > "/tmp/entrypoint" \
    && chmod +x "/tmp/entrypoint" \
    && :

# hadolint ignore=DL3008,DL3009
RUN : \
    && echo "========================================== INSTALL LATEST PYTHON ==========================================" \
    && DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:deadsnakes/ppa  \
    && DEBIAN_FRONTEND=noninteractive apt-get update  \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y python3.11 python3.11-dev python3.11-venv python3.11-dev \
    && DEBIAN_FRONTEND=noninteractive add-apt-repository --remove ppa:deadsnakes/ppa  \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && echo "==================================================== DONE ====================================================" \
    && :

RUN : \
    && echo "========================================== Docker Install ==========================================" \
    && curl -fsSL https://get.docker.com -o /tmp/get-docker.sh \
    && sh /tmp/get-docker.sh \
    && usermod -aG docker "${DEVENV_USERNAME}" \
    && rm /tmp/get-docker.sh \
    && :

USER "${DEVENV_USERNAME}"

RUN : \
    && echo "====================== INSTALL SDKMAN PIPX ===================" \
    && curl -s "https://get.sdkman.io" -o /tmp/sdkman \
    && bash /tmp/sdkman \
    && rm /tmp/sdkman \
    && python3.11 -m venv /tmp/_venv \
    && /tmp/_venv/bin/pip install --upgrade pip pipx \
    && /tmp/_venv/bin/pipx install pipx \
    && /tmp/_venv/bin/pipx install git+https://github.com/FlavioAmurrioCS/comma.git \
    && echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> ~/.bashrc \
    && rm -rf /tmp/_venv/bin/pipx \
    && :

ENTRYPOINT [ "/tmp/entrypoint" ]
CMD [ "/bin/bash" ]
