#curl -sL https://cli.openfaas.com | sudo sh


OPENFAAS_PASSWORD='admin'
MONGODB_ROOT_PASSWORD=deltaproject01

kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml
kubectl -n openfaas create secret generic basic-auth \
--from-literal=basic-auth-user=admin \
--from-literal=basic-auth-password=$OPENFAAS_PASSWORD
helm upgrade openfaas --install openfaas/openfaas --namespace openfaas -f stack.yml


#install mongodb
#arkade install mongodb
helm install mongodb bitnami/mongodb --set auth.rootPassword=$MONGODB_ROOT_PASSWORD

kubectl get pod -o wide