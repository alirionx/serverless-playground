```
pack build ghcr.io/alirionx/crud-example-python:latest \
  --buildpack paketo-buildpacks/python \
  --builder paketobuildpacks/builder-jammy-base

#OR via Dockerfile 
docker build -t ghcr.io/alirionx/crud-example-python:latest .
docker build -f Dockerfile-build -t ghcr.io/alirionx/crud-example-python:latest . # <= nuitka executable


docker push ghcr.io/alirionx/crud-example-python:latest

kubectl create secret docker-registry my-ghcr \
  --docker-server=https://ghcr.io/ \
  --docker-email=dquilitzsch@app-scape.de \
  --docker-username=alirionx \
  --docker-password=GehHe1m!

kubectl patch serviceaccount default -p "{\"imagePullSecrets\": [{\"name\": \"my-ghcr\"}]}"

kubectl apply -f kn-services.yaml

```