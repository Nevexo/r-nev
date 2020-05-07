FROM alpine

RUN apk add git

VOLUME [ "/mnt" ]

COPY git_runner.sh /git_runner.sh

CMD ["ash", "/git_runner.sh"]