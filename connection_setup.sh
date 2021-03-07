
OPENFAAS_URL='localhost:8080'

OPENFAAS_GATEWAY_NAME=$(kubectl get pod -n openfaas -o custom-columns=POD:metadata.name  | grep gateway) 
OPENFAAS_PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)

kubectl port-forward -n openfaas $OPENFAAS_GATEWAY_NAME 8080:8080 &
faas-cli login --password $OPENFAAS_PASSWORD


#deploy function
faas-cli up -f stack.yml

mongodb_name=$(kubectl get pod -o custom-columns=POD:metadata.name  | grep mongo) 
kubectl port-forward $mongodb_name 27017:27017 &

MONGODB_CONNECTION_URI = "mongodb://root:deltaproject01@localhost:27017"

echo "======================================================================="
echo "Variables"
echo "======================================================================="
echo "OPENFAAS_PASSWORD - " $OPENFAAS_PASSWORD
echo "OPENFAAS_GATEWAY_NAME - " $OPENFAAS_GATEWAY_NAME
echo "MONGODB_NAME - " $mongodb_name
echo "MONGODB_CONNECTION_URI - $MONGODB_CONNECTION_URI


