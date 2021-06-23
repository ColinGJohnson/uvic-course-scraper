# set base image (host OS)
FROM python:3.8

# the successive commands will be executed in this directory
WORKDIR /usr/src/app

# copy the content of the local src directory to the working directory
ADD src/* ./

# install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# install aws cli (see: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

# command to run on container start
RUN chmod +x run.sh
CMD [ "./run.sh" ]
