# Delta Data Engineering Test

## Table of content

## **Assignment**

We currently integrate with multiple data providers, all providing price data.

These integrations range from real-time data feeds to periodically polling APIs for all available data.

Roughly speaking, you can assume that these integrations provide a non-stop flow of the following data events:

```tsx
struct PriceEvent {
    baseCurrency: string;
    quoteCurrency: string;
    exchange: string;
    price: float64;
    baseVolumeLast24h: float64;
    quoteVolumeLast24h: float64;
    timestampInMs: uint64;
}
```

Your assignment consists on designing an optimal way to ingest this data, process it and store it somewhere given the following requirements:

1. The most recent price must be retrievable, given a certain `(baseCurrency, quoteCurrency, exchange)` tuple (or an array of them).
2. Historical data must be retrievable, but the granularity can be more coarse the older the data is (generally only [OHLC](https://en.wikipedia.org/wiki/Open-high-low-close_chart) is kept, make a proposal). This will be queried again in a key-value (same primary key as above) fashion, but time-based range queries are possible as well.
3. A list of all possible exchanges, their pairs (`(baseCurrency, quoteCurrency)`) and the last time a price point has been observed should be retrievable.
4. Optional: a list of the most recent prices grouped by `baseCurrency` (you can assume a mapping of `baseCurrency` -> `(quoteCurrency, exchange)` is available) should be retrievable.

You are expected to come up with a design plan on how to tackle this data ingestion and querying assignment. Next to that, a PoC of the data ingestion and querying components - demonstrating that your approach works - is required as well.

Scale-wise, you can expect between 50k - 150k incoming price events every couple of seconds. If possible, make separate proposals on how to tackle extra incoming load (read vs write).

You can assume a 70/30 ratio of reads/writes, where the recency of the data correlates with how hot it is.

### **Technologies & tools**

You are free to use all the tools that you want or feel you need to!

However, since we use JavaScript (TypeScript is preferred) and Node.JS (latest LTS) at Delta, it is strongly recommended to write your application code using this environment.

### **Tips**

- Start small and build up gradually. Try to document all your trains of thought, even if they seem insignificant or stupid.
- If possible, provide multiple alternatives and explain why the one is preferred over the other.
- Provide metrics proving that your suggestion solution works well.
- Keep resource and budget constraints in mind, the lower the better.
- KISS, when possible. Simplicity trumps complexity.
- Be prepared to get questions later about choices you've made.

## **Timeframe**

Spend as much time on this as you want, but don't go overboard. Again, keep it as simple as possible while still fulfilling the requirements.

## **Delivery**

Send us a link to an accessible git repository so we can checkout your design and code.

Please make sure your PoC runs in a Docker environment (foresee a `docker-compose.yml` file).

## **Questions?**

Feel free to contact us if something would not be clear.

## 

[Requirements](https://www.notion.so/1e93bb516a5e48caaee3484c3aa65406)

## Architecture

![Delta%20Data%20Engineering%20Test%20b3c8244c753941af8908be6c8059663a/delta_architecture_POC.png](Delta%20Data%20Engineering%20Test%20b3c8244c753941af8908be6c8059663a/delta_architecture_POC.png)

### Apache Kafka

Apache Kafka is an open-source distributed streaming platform. The platform is run as a cluster on one or more servers, called brokers. It functions as a publish/subscribe messaging queue. It stores the streams of data records in a fault-tolerant durable way on topics. It is mainly used to build a real-time streaming data pipeline.

Kafka stores key-value messages that come from producers (publishers). The data can be partitioned into different “partitions” with different “topics”. Consumers (subscribers) are able to read messages from the partitions. The partitions are replicated across multiple brokers, this allows the system to be fault tolerant.

![Delta%20Data%20Engineering%20Test%20b3c8244c753941af8908be6c8059663a/Untitled.png](Delta%20Data%20Engineering%20Test%20b3c8244c753941af8908be6c8059663a/Untitled.png)

The key abstraction in Kafka is the topic. Producers publish their records to a topic, and consumers subscribe to one or more topics. A Kafka topic is just a sharded write-ahead log. Producers append records to these logs and consumers subscribe to changes. Each record is a key/value pair. 

Why Kafka? 

### Kafka Connect

Kafka Connect is an open-source framework that allows the connection of Kafka with external systems such as databases, key-value stores, search indexes, and file systems. Using Kafka Connect you can use existing connector implementations for common data sources and sinks to move data into and out of Kafka.

In this project we have a sink connector that allows us to deliver data from Kafka topics into a MongoDb database.

### Apache Zookeeper

ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services. All of these kinds of services are used in some form or another by distributed applications.

ZooKeeper keeps track of the status of the Kafka cluster and about the Kafka topics, partitions, etc.

The data within Zookeeper is divided across multiple collection of nodes and this is how it achieves its high availability and consistency. In case a node fails, Zookeeper can perform instant failover migration; e.g. if a master node fails, a new one is selected in real-time by polling within an ensemble. A client connecting to the server can query a different node if the first one fails to respond.

### OpenFaaS

OpenFaas is a platform that allows us to run short-running tasks with an http endpoint (webhook). It creates a Function as a Service like Amazon Lambda or Azure Functions. It is a practical and serverless platform that supports various programming languages like java, c#, node.js etc. The applications that are being deployed are called functions, there are based on Docker images. The OpenFaas environment is deployed in our Kubernetes cluster. 

// to do debate on openfaas and alternatives

### Kubernetes

Kubernetes is a powerful container management tool that automates the deployment and management of containers

- **Scalability.** Software can be deployed for the first time in a scale-out manner across Pods, and deployments can be scaled in or out at any time.
- **Visibility.** Identify completed, in-process, and failing deployments with status querying capabilities.
- **Time savings.** Pause a deployment at any time and resume it later.
- **Version control.** Update deployed Pods using newer versions of application images and roll back to an earlier deployment if the current version is not stable.
- Independent. Kubernetes itself is independent on where it runs. It can run on any major cloud provider (AWS, Google, Azure) and even on-premise.

Kubernetes clusters can run on EC2 and integrate with services such as Amazon Elastic Block Storage, Elastic Load Balancing, Auto Scaling Groups, and so on.

### MongoDB

### Handling Hot Data

Real time data streaming and handling Hot Data

//todo

```python

{
    timestamp_id : uint64,
    priceEvent: {
        baseCurrency: string;
        quoteCurrency: string;
        exchange: string;
        price: float64;
        baseVolumeLast24h: float64;
        quoteVolumeLast24h: float64;
    }
}

#example
{
    "timestampInMs" : 1614518938577 ,
    "priceEvent": {
        "baseCurrency": "BTC",
        "quoteCurrency": "USDC",
        "exchange": "Binance",
        "price": "46450",
        "baseVolumeLast24h": "2095.19824100",
        "quoteVolumeLast24h": "95422969.85662475"
    }
}
```

# Minimum Viable Product

For this POC I limited myself in developing an MVP. This includes OpenFaaS server-less functions and a connection with MongoDB. Both components running in a Kubernetes cluster for scaling. 

## MVP Architecture

![Delta%20Data%20Engineering%20Test%20b3c8244c753941af8908be6c8059663a/asis_mvp_architecture.png](Delta%20Data%20Engineering%20Test%20b3c8244c753941af8908be6c8059663a/asis_mvp_architecture.png)

## Instructions

I prepared a short video to show the installation process of my POC. 

[https://youtu.be/CINoB0dy8go](https://youtu.be/CINoB0dy8go)

### Prerequisites

Before we start, you’ll need access to the following:

- Kubernetes - install with your preferred local tooling such as KinD, minikube, or k3d. Or use a cloud service like Amazon EKS, GKE or DigitalOcean Kubernetes. A single VM running k3s is also fine.
- To start your minikube

```bash
minikube start
//or assign more memory run $ minikube start --memory=8192 --cpus=4
```

- A running Docker Deamon. You can check this by running $docker ps.

### Setup

Clone following git repo

```bash
git clone https://github.com/Crielz/deltaproject.git
```

Download and install Openfaas.

```bash
curl -sL https://cli.openfaas.com | sudo sh
```

Make sure you are in directory "mongodb-function" and execute bootstrap script.

```bash
source bootstrap.sh

```

Replace "nathancriel/" prefix from Docker Hub in stack.yml with your own account

```bash
image: <your-docker-username>/functions:latest
```

Check if Openfaas and mongoDB are running

```bash
kubectl get pod -n openfaas -o wide
```

When all pods are in a running state, execute following command:

```bash
source connection_setup.sh
```

If you see an error that refers to a missing node10-express template, try pulling the template with:

```tsx
faas template pull https://github.com/openfaas-incubator/node10-express-template
```

Test if the OpenFaaS functions works with a simple curl command. 

```bash
curl http://$OPENFAAS_URL/function/insert-priceevent
```

Download a load testing tool. I use go, this requires an i[nstallation of Go](https://golang.org/dl/).

```bash
$ go get -u github.com/rakyll/hey

$ ~/go/bin/hey -m POST  \
  -H "Content-Type: application/json" \
  -n 10000 -c 10 http://$OPENFAAS_URL/function/insert-priceevent
```

To view documents in MongoDB, download a MongoDB client and get the connection URI by executing;

```bash
echo $MONGODB_CONNECTION_URI
```

## Read Data Demonstration

[https://www.youtube.com/watch?v=izJTIodg4PM](https://www.youtube.com/watch?v=izJTIodg4PM)

# Resources/ links

[Apache Kafka](https://kafka.apache.org/quickstart)

[Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines)](https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines)

[Apache Kafka with Kubernetes - Provision and Performance](https://medium.com/swlh/apache-kafka-with-kubernetes-provision-and-performance-81c61d26211c#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6ImZkYjQwZTJmOTM1M2M1OGFkZDY0OGI2MzYzNGU1YmJmNjNlNGY1MDIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYmYiOjE2MTM1NTM0NjAsImF1ZCI6IjIxNjI5NjAzNTgzNC1rMWs2cWUwNjBzMnRwMmEyamFtNGxqZGNtczAwc3R0Zy5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwODQzODA5MzU1NjE2MjYwNzkyMSIsImVtYWlsIjoicGVkYWZpeEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXpwIjoiMjE2Mjk2MDM1ODM0LWsxazZxZTA2MHMydHAyYTJqYW00bGpkY21zMDBzdHRnLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwibmFtZSI6Ik5hdGhhbiBDcmllbCIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS0vQU9oMTRHal9OM08yd09yM0tycGluX3V2QmJhd0Q3MlN6Sy1hNGxTM21WSVI9czk2LWMiLCJnaXZlbl9uYW1lIjoiTmF0aGFuIiwiZmFtaWx5X25hbWUiOiJDcmllbCIsImlhdCI6MTYxMzU1Mzc2MCwiZXhwIjoxNjEzNTU3MzYwLCJqdGkiOiIwZDQ2MGRmMGE4YTdjMDNlYzVhNTQ0ZGM5NjhjNWViYzNiMTE3YzQwIn0.X7E9IXOgfCvB5br5VOrPX9Me0o1R_sQoY3EGnYRdRn3e5TLfVbF0kdX3_XAp22v10DIXXsMY6vQQFSiBWfC33ulXnBwIYDiroV4Nuv8R-_YLCCS_kOepchgIf7m1WpaM_JBJ_ttZwuqpf0LkNvl7GgdcsSi-ay_5DaovhIa26x-3R2rnzi1PNvegb2ClR0H5iBSSh3w_Xvw94cby5gtRvwf7fzKlqzo8W0IETf6qpY6HeaeuBLm34rit3nBiw4lsl3JSrIKYYbXtqKDj-O0NQkkGwerCn8YlRJAWMLyVgTiwwfRFbgF8aL5yJUdgKiMU2Pc-GD0HXDMxRVucU4g4mg)

[Build a Scalable, Fault-Tolerant Messaging Cluster on Kubernetes with Apache Kafka and MongoDB](https://docs.bitnami.com/tutorials/build-messaging-cluster-apache-kafka-mongodb-kubernetes/)

[Managing MongoDB on docker with docker-compose](https://medium.com/faun/managing-mongodb-on-docker-with-docker-compose-26bf8a0bbae3)