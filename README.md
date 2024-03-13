# payabl. Backend Engineer Code Assignment

## Requisites

You must have Python 3.11 installed along with docker and docker-compose in your machine to develop this assignment

## Objective

Your main task is to create a simple version of banking application using microservice architecture 
using kafka, python, fastapi, aiokafka (or any other client you would like to use).

## Acceptance criteria

* You should have 3 services, payment-service, account-service, report-service
  * Account service is used for setup an account with an IBAN (you don't need to generate your own iban, it can be a field where you put some random iban from http://randomiban.com/?country=Netherlands) and balance
  * Payment service is used for making outgoing payments and accept incoming payments from webhook.
  * Report service is used to generate csv reports.
* Each service should run own DB and have own docker image
* There should be docker-compose file which allows to run all the services, kafka and DBs at ones
* There should be example of .env file for each service

### Webhook example

In order to implement webhook it should be a POST endpoint that returns 200 status code.
This endpoint should accept following request body

```json
{
  "sender_iban": "NL43ABNA6922895703",
  "sender_name": "Sender name",
  "sender_bic": "ABNANL2AXXX",
  "receiving_iban": "PL43109024029982137336636247",
  "external_id": "23",
  "amount": "1000",
  "currency": "EUR",
  "reference": "323443221346223",
  "purpose": "Test incoming"
}
```

### Report example

Each report should be created for given account.
The report should contain following columns
```
IBAN, TRANSACTION_ID, SENDER_IBAN, SENDER_BIC, SENDER_NAME, AMOUNT, CURRENCY, PURPOSE
```

### Payments logic

There are 2 types of payments, outgoing payment and incoming payment.

Outgoing can be created by user (for this task you don't need to implement any auth logic, so let's imagine that anyone can access that account).
That payment should reduce the balance

Incoming can be created via webhook and that payment should increase your balance

## Submission

* Once you are done, include a CHANGELOG.md file in which you can list the features you have implemented in the project 
* You can then compress the repository into a zip file - without the dependencies, please - and send it back to the recruiter that provided you with this assignment. 
* Feel free to write any other documentation you feel necessary to clarify your thougts, decisions and processes while developing.

If you need any clarification or have any questions do not hesitate to contact your recruiter. Ensure the you undestand the assignemnt prior to starting it.

Good luck!