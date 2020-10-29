
# vim:set ft=dockerfile:

FROM cimg/python:3.7.9

SHELL ["/bin/bash", "-c"]

# RUN 

# Dockerfile will pull the latest LTS release from cimg-node.
RUN curl -sSL "https://raw.githubusercontent.com/CircleCI-Public/cimg-node/master/ALIASES" -o nodeAliases.txt && \
	NODE_VERSION=$(grep "lts" ./nodeAliases.txt | cut -d "=" -f 2-) && \
	curl -L -o node.tar.xz "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" && \
	sudo tar -xJf node.tar.xz -C /usr/local --strip-components=1 && \
	rm node.tar.xz nodeAliases.txt && \
	sudo ln -s /usr/local/bin/node /usr/local/bin/nodejs

ENV YARN_VERSION 1.22.4
RUN curl -L -o yarn.tar.gz "https://yarnpkg.com/downloads/${YARN_VERSION}/yarn-v${YARN_VERSION}.tar.gz" && \
	sudo tar -xzf yarn.tar.gz -C /opt/ && \
	rm yarn.tar.gz && \
	sudo ln -s /opt/yarn-v${YARN_VERSION}/bin/yarn /usr/local/bin/yarn && \
	sudo ln -s /opt/yarn-v${YARN_VERSION}/bin/yarnpkg /usr/local/bin/yarnpkg

RUN wget https://github.com/ethereum/solidity/releases/download/v0.5.17/solc-static-linux \
 && chmod +x solc-static-linux \
 && sudo mv solc-static-linux /usr/bin/solc

RUN sudo useradd -m slither
USER slither

COPY --chown=slither:slither . /home/slither/slither
WORKDIR /home/slither/slither

RUN python3 setup.py install --user
ENV PATH="/home/slither/.local/bin:${PATH}"
CMD /bin/bash