# Slackbot

This project is a bot for slack that will send a message when a new row added on googlesheet.

Prerequisites
Python 3.8+
Docker (for containerization)
Local Setup
Clone the repository

### Copy code

`git clone https://github.com/farazabir/slackbot.git`

### Navigate to the directory :

`cd slackbot`

### Make a .env file

`SLACK_TOKEN= ur slack token`

`SLACK_CHANNEL= channel id`

## Set Up Virtual Environment:

### Create and activate a virtual environment

`virtualenv venv`

`source venv/bin/activate`

# Docker Setup

## Build the Docker image

` docker compose up --build`

## After building the image, run the container with:

## Access the app by navigating to http://localhost:9999 in your web browser.
