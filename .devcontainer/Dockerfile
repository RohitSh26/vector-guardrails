# Base: official devcontainers Python image (Debian + 'vscode' user)
FROM mcr.microsoft.com/devcontainers/python:3.11

# System packages you’ll likely need (build tools, git, curl, etc.)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates bash-completion locales less \
    build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set UTF-8 locale
RUN sed -i 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Prepare a workspace directory (devcontainer.json binds the local repo here)
RUN mkdir -p /workspaces/vector-guardrails
WORKDIR /workspaces/vector-guardrails

# Make sure the 'vscode' user owns the workspace
RUN chown -R vscode:vscode /workspaces

# Use non-root going forward
USER vscode

# Ensure ~/.local/bin is on PATH for the vscode user (uv installers use it)
ENV PATH="/home/vscode/.local/bin:${PATH}"
