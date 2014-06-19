#!/usr/bin/env python

#This is the program that runs on each car and takes input from the control laptop

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.1.204'))
channel = connection.channel()
channel.queue_declare(queue='hello')

def CBMethod(data):
    print " [x] Sent {0}".format(data)
    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body=data)

connection.close()
