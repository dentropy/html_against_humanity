FROM alpine

RUN apk add python3
RUN apk add curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py 
RUN rm get-pip.py
ADD ./server $HOME/html-against-humanity/
RUN pip install -r /html-against-humanity/requirements.txt
CMD python3 /html-against-humanity/webserver.py
# CMD ["/bin/sh", "-c", "while true; do sleep 1000; done"]