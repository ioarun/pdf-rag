# Use the official Ubuntu image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Update and install basic stuff
RUN apt-get update && apt-get install -y \
    curl \
    nano \
    python3 \
    pip 

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /workspace

COPY requirements.txt /workspace/requirements.txt
RUN uv pip install --system -r requirements.txt

COPY . .

# Expose port for Jupyter
EXPOSE 8888

# Run Jupyter when the container starts
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
