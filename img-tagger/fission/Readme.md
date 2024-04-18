```
fission environment create --name go-image-tagger --image fission/go-env-1.17 --builder fission/go-builder-1.17
# Add Envs Minio Envs afterwards via "kubectl edit environment go-image-tagger"

# =>>>> OR directly via kubectl apply <<<<=
kubectl apply -f go-image-tagger-environment.yaml


fission fn create --name image-tagger --env go-image-tagger --entrypoint Handler --src src/go.mod --src src/go.sum --src src/main.go  

fission httptrigger create --name image-tagger-post --method POST --url "/image-tagger" --function image-tagger

curl --location 'http://192.168.10.162/image-tagger' --form 'image=@"/mnt/c/Users/dquil/Pictures/cliffs-of-moher.jpg"'

```