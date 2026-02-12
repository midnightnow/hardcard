# HardCard Development Container
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Build essentials
        build-essential \
        gcc \
        g++ \
        make \
        cmake \
        # Python development
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        # PostgreSQL development
        postgresql-client \
        libpq-dev \
        # Redis tools
        redis-tools \
        # Security tools
        gnupg \
        openssh-client \
        ca-certificates \
        # Network tools
        curl \
        wget \
        httpie \
        netcat \
        dnsutils \
        iputils-ping \
        # Development tools
        vim \
        tmux \
        htop \
        tree \
        jq \
        ripgrep \
        fd-find \
        bat \
        # Version control
        git-flow \
        git-lfs \
        # Container tools (installed by feature)
        # docker-ce-cli \
        # docker-compose-plugin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install global Python packages
RUN pip3 install --no-cache-dir \
    # Development tools
    ipython \
    ipdb \
    rich \
    # Testing tools  
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-mock \
    pytest-benchmark \
    hypothesis \
    # Code quality
    black \
    isort \
    flake8 \
    mypy \
    pylint \
    bandit \
    safety \
    # Documentation
    mkdocs \
    mkdocs-material \
    # Database tools
    alembic \
    sqlalchemy-utils \
    # API tools
    httpx \
    # Performance monitoring
    py-spy \
    memory-profiler \
    line-profiler

# Install Node.js global packages
RUN npm install -g \
    # Package managers
    yarn \
    pnpm \
    # Development tools
    nodemon \
    ts-node \
    typescript \
    # Testing
    jest \
    @playwright/test \
    # Code quality
    eslint \
    prettier \
    # API development
    @stoplight/prism-cli \
    # Security
    snyk

# Install Rust (for performance-critical tools)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install performance tools written in Rust
RUN cargo install \
    bat \
    exa \
    tokei \
    hyperfine \
    bandwhich \
    grex

# Install Go tools
RUN go install github.com/rakyll/hey@latest && \
    go install github.com/securego/gosec/v2/cmd/gosec@latest && \
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Install k6 for load testing
RUN gpg -k && \
    gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69 && \
    echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | tee /etc/apt/sources.list.d/k6.list && \
    apt-get update && \
    apt-get install -y k6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install GitHub CLI extensions
RUN gh extension install github/gh-copilot || true && \
    gh extension install dlvhdr/gh-dash || true && \
    gh extension install meiji163/gh-notify || true

# Set up shell
COPY config/.zshrc /home/vscode/.zshrc
COPY config/.aliases /home/vscode/.aliases
RUN chown -R vscode:vscode /home/vscode

# Install Oh My Zsh plugins
RUN git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-completions

# Create workspace directory
RUN mkdir -p /workspace && chown -R vscode:vscode /workspace

# Switch to non-root user
USER vscode

# Set working directory
WORKDIR /workspace

# Keep container running
CMD ["sleep", "infinity"]