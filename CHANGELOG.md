# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
 - account-service to set up an account with an IBAN and balance
 - payment-service to make outgoing payments and accept incoming payments from webhook
 - report-service to generate csv reports
 - docker-compose file which allows to run all the services, kafka and DBs at once
 - added schema.png to visualize app architecture