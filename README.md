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

## Backlog
![](./diagram/backlog.png)

## Architecture
![](./diagram/delta_architecture_POC.png)


# Introduction

In this READ.me file I give a small introduction on the different services I use in my solution. I suggest going over my approach and train of thought during the second interview.  To get your hands dirty please refer to the instructions segment where I will guide you through the installation of my POC. I prepared a short video to demonstrate how I set it up on my local machine.

### Apache Kafka

Apache Kafka is an open-source distributed streaming platform. The platform is run as a cluster on one or more servers, called brokers. It functions as a publish/subscribe messaging queue. It stores the streams of data records in a fault-tolerant durable way on topics. It is mainly used to build a real-time streaming data pipeline.

Kafka stores key-value messages that come from producers (publishers). The data can be partitioned into different “partitions” with different “topics”. Consumers (subscribers) are able to read messages from the partitions. The partitions are replicated across multiple brokers, this allows the system to be fault-tolerant.

![](./diagram/apache_kafka_producer_consumer.png)


The key abstraction in Kafka is the topic. Producers publish their records to a topic, and consumers subscribe to one or more topics. A Kafka topic is just a sharded write-ahead log. Producers append records to these logs and consumers subscribe to changes. Each record is a key/value pair. 

### Kafka Connect

Kafka Connect is an open-source framework that allows the connection of Kafka with external systems such as databases, key-value stores, search indexes, and file systems. Using Kafka Connect you can use existing connector implementations for common data sources and sinks to move data into and out of Kafka.

In this project, we have a sink connector that allows us to deliver data from Kafka topics into a MongoDB database.

### Apache Zookeeper

ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services. All of these kinds of services are used in some form or another by distributed applications.

ZooKeeper keeps track of the status of the Kafka cluster and about the Kafka topics, partitions, etc.

The data within Zookeeper is divided across multiple collections of nodes and this is how it achieves its high availability and consistency. In case a node fails, Zookeeper can perform instant failover migration; e.g. if a master node fails, a new one is selected in real-time by polling within an ensemble. A client connecting to the server can query a different node if the first one fails to respond.

### OpenFaaS

OpenFaas is a platform that allows us to run short-running tasks with an HTTP endpoint (Webhook). It creates a Function as a Service like Amazon Lambda or Azure Functions. It is a practical and server-less platform that supports various programming languages like java, c#, Node.js, etc. The applications that are being deployed are called functions, there are based on Docker images. The OpenFaas environment is deployed in our Kubernetes cluster. 

### Kubernetes

Kubernetes is a powerful container management tool that automates the deployment and management of containers

- **Scalability.** Software can be deployed for the first time in a scale-out manner across Pods, and deployments can be scaled in or out at any time.
- **Visibility.** Identify completed, in-process, and failing deployments with status querying capabilities.
- **Time savings.** Pause a deployment at any time and resume it later.
- **Version control.** Update deployed Pods using newer versions of application images and roll back to an earlier deployment if the current version is not stable.
- Independent. Kubernetes itself is independent on where it runs. It can run on any major cloud provider (AWS, Google, Azure) and even on-premise.

Kubernetes clusters can run on EC2 and integrate with services such as Amazon Elastic Block Storage, Elastic Load Balancing, Auto Scaling Groups, and so on.

### MongoDB

MongoDB  is an open-source database that uses a doc-oriented database written in C++ and it is a non-structured query language and in today's it is the most powerful database. in MongoDB, you can create multiple databases and each database can have multiple collections. 

### Handling Hot Data

Real-time data streaming and handling Hot Data. To tackle this I have 2 propositions:

1. MongoDB Aggregation Pipeline & Sharding
2. Apache KSQL

To optimize read/write capabilities I propose structuring the priceEvent in the following code snippet. 

```python

# how data is inserted in mongoDB
{
"timestampInMs" : Date.now() ,
"priceEvent": {
    "baseCurrency": baseCurrencies[Math.floor(Math.random() * baseCurrencies.length)],
    "quoteCurrency": quoteCurrencies[Math.floor(Math.random() * quoteCurrencies.length)],
    "exchange": exchanges[Math.floor(Math.random() * exchanges.length)],
    "price": Math.floor(Math.random()*1000),
    "baseVolumeLast24h": "2095.19824100",
    "quoteVolumeLast24h": "95422969.85662475"
    }
}

# how data will be transformed using the aggregation pipeline
"priceEvent": {
    "baseCurrency": "BTC"
    "quoteCurrency": "USDC",
    "exchange": "binance",
    "baseVolumeLast24h": "2095.19824100",
    "quoteVolumeLast24h": "95422969.85662475"
    "timestampCol": {
        1615184524097: 48550,
        1615184524128: 48660,
        1615184524097: 48330,
        1615184524149: 48485,
        1615184524154: 48600
        }
    }
    

# final structure 
{
"priceEvent": {
    "baseCurrency": "BTC"
    "quoteCurrency": "USDC",
    "exchange": "binance",
    "baseVolumeLast24h": "2095.19824100",
    "quoteVolumeLast24h": "95422969.85662475"
    "minTimestampInMs": 1615184524097,
    "maxTimestampInMs": 1615184524154,
    "open": 48550,
    "high": 48660,
    "low": 48330,
    "close": 48600   
    }

}
```

# Minimum Viable Product

For this POC I limited myself in developing an MVP. This includes OpenFaaS server-less functions and a connection with MongoDB. Both components running in a Kubernetes cluster for scaling. 

## MVP Architecture

![](./diagram/asis_mvp_architecture.png)

![Delta%20Data%20Engineering%20Test%209bac4216379f45f9bc402d31c547a142/asis_mvp_architecture.png]
## Instructions

I prepared a short video to show the installation process of my POC. 

[https://youtu.be/CINoB0dy8go](https://youtu.be/CINoB0dy8go)

### Prerequisites

Before we start, you’ll need access to the following:

- Kubernetes - install with your preferred local tooling such as KinD, Minikube, or k3d. Or use a cloud service like Amazon EKS, GKE, or DigitalOcean Kubernetes. A single VM running k3s is also fine.
- To start your Minikube

```bash
minikube start --memory=4096 --cpus=4
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

Make sure you are in the directory "deltaproject" and execute the bootstrap script.

```bash
cd deltaproject
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

When all pods are in a running state, execute the following command:

```bash
source connection_setup.sh
```

If you see an error that refers to a missing node10-express template, try pulling the template with:

```tsx
faas template pull https://github.com/openfaas-incubator/node10-express-template
```

Test if the OpenFaaS functions work with a simple curl command. 

```bash
curl http://$OPENFAAS_URL/function/insert-priceevent
```

Download a load testing tool. I use GO, this requires an [installation of Go.](https://golang.org/dl/)

```bash
$ go get -u github.com/rakyll/hey

$ ~/go/bin/hey -m POST  \
  -H "Content-Type: application/json" \
  -n 1000 -c 10 http://$OPENFAAS_URL/function/insert-priceevent
```

To view documents in MongoDB, download a MongoDB client and get the connection URI by executing;

```bash
mongodb://root:deltaproject01@localhost:27017
```

## Read Data Demonstration

[https://www.youtube.com/watch?v=izJTIodg4PM](https://www.youtube.com/watch?v=izJTIodg4PM)

# Resources/ links

[Apache Kafka](https://kafka.apache.org/quickstart)

[Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines)](https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines)

[Apache Kafka with Kubernetes - Provision and Performance](https://medium.com/swlh/apache-kafka-with-kubernetes-provision-and-performance-81c61d26211c#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6ImZkYjQwZTJmOTM1M2M1OGFkZDY0OGI2MzYzNGU1YmJmNjNlNGY1MDIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYmYiOjE2MTM1NTM0NjAsImF1ZCI6IjIxNjI5NjAzNTgzNC1rMWs2cWUwNjBzMnRwMmEyamFtNGxqZGNtczAwc3R0Zy5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwODQzODA5MzU1NjE2MjYwNzkyMSIsImVtYWlsIjoicGVkYWZpeEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXpwIjoiMjE2Mjk2MDM1ODM0LWsxazZxZTA2MHMydHAyYTJqYW00bGpkY21zMDBzdHRnLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwibmFtZSI6Ik5hdGhhbiBDcmllbCIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS0vQU9oMTRHal9OM08yd09yM0tycGluX3V2QmJhd0Q3MlN6Sy1hNGxTM21WSVI9czk2LWMiLCJnaXZlbl9uYW1lIjoiTmF0aGFuIiwiZmFtaWx5X25hbWUiOiJDcmllbCIsImlhdCI6MTYxMzU1Mzc2MCwiZXhwIjoxNjEzNTU3MzYwLCJqdGkiOiIwZDQ2MGRmMGE4YTdjMDNlYzVhNTQ0ZGM5NjhjNWViYzNiMTE3YzQwIn0.X7E9IXOgfCvB5br5VOrPX9Me0o1R_sQoY3EGnYRdRn3e5TLfVbF0kdX3_XAp22v10DIXXsMY6vQQFSiBWfC33ulXnBwIYDiroV4Nuv8R-_YLCCS_kOepchgIf7m1WpaM_JBJ_ttZwuqpf0LkNvl7GgdcsSi-ay_5DaovhIa26x-3R2rnzi1PNvegb2ClR0H5iBSSh3w_Xvw94cby5gtRvwf7fzKlqzo8W0IETf6qpY6HeaeuBLm34rit3nBiw4lsl3JSrIKYYbXtqKDj-O0NQkkGwerCn8YlRJAWMLyVgTiwwfRFbgF8aL5yJUdgKiMU2Pc-GD0HXDMxRVucU4g4mg)

[Build a Scalable, Fault-Tolerant Messaging Cluster on Kubernetes with Apache Kafka and MongoDB](https://docs.bitnami.com/tutorials/build-messaging-cluster-apache-kafka-mongodb-kubernetes/)

[Managing MongoDB on docker with docker-compose](https://medium.com/faun/managing-mongodb-on-docker-with-docker-compose-26bf8a0bbae3)