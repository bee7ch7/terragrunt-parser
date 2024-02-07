FROM python:3.12-alpine

ENV TF_VERSION=1.7.0
ENV TG_VERSION=v0.50.14
ENV PATH="${PATH}:/app"

WORKDIR /app
COPY requirements.txt terragrunt_parser.py /app/
ADD functions /app/functions

RUN pip install -r requirements.txt

RUN apk update && apk add unzip wget openssh-client git --no-cache \
  && wget --quiet https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip \
  && unzip terraform_${TF_VERSION}_linux_amd64.zip \
  && rm -f terraform_${TF_VERSION}_linux_amd64.zip \
  && chmod +x /app/terraform

RUN wget --quiet https://github.com/gruntwork-io/terragrunt/releases/download/${TG_VERSION}/terragrunt_linux_amd64 \
  && mv terragrunt_linux_amd64 /app/terragrunt \
  && chmod +x /app/terragrunt
