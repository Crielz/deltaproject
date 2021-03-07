"use strict"

const MongoClient = require('mongodb').MongoClient
, assert = require('assert');

var clientsDB;  // Cached connection-pool for further requests. 

var exchanges = Array("binance", "coinbase", "kucoin", "kraken")
var baseCurrencies = Array("BTC", "ETH", "DOT", "ADA")
var quoteCurrencies = Array("USDC", "USDT", "EUR", "USD")

module.exports = (event, context) => {
    prepareDB()
    .then((users) => {

        const record = {
            "timestampInMs" : Date.now() ,
            "priceEvent": {
                "baseCurrency": baseCurrencies[Math.floor(Math.random() * baseCurrencies.length)],
                "quoteCurrency": quoteCurrencies[Math.floor(Math.random() * quoteCurrencies.length)],
                "exchange": exchanges[Math.floor(Math.random() * exchanges.length)],
                "price": Math.floor(Math.random()*1000),
                "baseVolumeLast24h": "2095.19824100",
                "quoteVolumeLast24h": "95422969.85662475"
                }
        };

        users.collection("priceCollection").insertOne(record, (insertErr) => {
            if(insertErr) {
                return context.fail(insertErr.toString());
            }

            const result =  {
                status: "Insert  of record: "+ JSON.stringify(record)
            };
    
            context
                .status(200)
                .succeed(result);
        });
    })
    .catch(err => {
        context.fail(err.toString());
    });
}

const prepareDB = () => {
    const url = "mongodb://root:"+process.env.password+ "@" + process.env.mongo + ":27017"

    return new Promise((resolve, reject) => {
        if(clientsDB) {
            console.error("DB already connected.");
            return resolve(clientsDB);
        }

        console.error("DB connecting");

        MongoClient.connect(url, (err, database) => {
            if(err) {
                return reject(url, err)
                //return reject(err)
            }
    
            clientsDB = database.db("prices");
            return resolve(clientsDB)
        });
    });
}

