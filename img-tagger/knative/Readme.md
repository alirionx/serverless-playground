```
pack build ghcr.io/alirionx/image-tagger-go:latest \
  --buildpack paketo-buildpacks/go \
  --builder paketobuildpacks/builder-jammy-base

#OR via Dockerfile 
docker build -t ghcr.io/alirionx/image-tagger-go:latest .


docker push ghcr.io/alirionx/image-tagger-go:latest

kubectl create secret docker-registry my-ghcr \
  --docker-server=https://ghcr.io/ \
  --docker-email=dquilitzsch@app-scape.de \
  --docker-username=alirionx \
  --docker-password=GehHe1m!

kubectl patch serviceaccount default -p "{\"imagePullSecrets\": [{\"name\": \"my-ghcr\"}]}"

kubectl apply -f kn-service.yaml

```