FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash coreutils git procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/ /app/

RUN mkdir -p /app/bin /app/site/releases /app/state /app/tmp \
    && git config --global init.defaultBranch main \
    && git config --global user.email solver@example.invalid \
    && git config --global user.name "tb-hard solver" \
    && git init --bare /app/repo.git \
    && chmod +x /app/bin/deploy.sh /app/bin/gitopsctl /app/repo.git/hooks/post-receive \
    && /app/bin/gitopsctl init

CMD ["/bin/bash"]
