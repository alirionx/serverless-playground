FROM ubuntu:jammy AS build
RUN apt update && apt install -y golang-go ca-certificates
WORKDIR /app
ADD src/* /app/
RUN go build -o /app/image-tagger

FROM ubuntu:jammy
RUN apt update && apt install -y ca-certificates
WORKDIR /app
RUN cd /app
COPY --from=build /app/image-tagger /app/image-tagger
CMD ["/app/image-tagger"]