FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl zip unzip bash && \
    curl -s "https://get.sdkman.io" | bash && \
    bash -c "source /root/.sdkman/bin/sdkman-init.sh && sdk install java"

ENV JAVA_HOME=/root/.sdkman/candidates/java/current
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /app

COPY . .

RUN pip install -e .

CMD ["run-app"]