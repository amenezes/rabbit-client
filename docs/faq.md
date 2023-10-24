## **Why should I use rabbit-client?**

`rabbit-client` provides a high level abstraction to consume and produce asynchronous events with some level of warranty that event don't will be lost in case of failures.

## **What type of job can I use?**

The `Subscribe` class use a `task` that's nothing more that an awaitable. This will be executed when a event is received by queue, so can you use a task to process IO or [CPU bound jobs](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor).

## **Why use Dead Letter Exchange?**

A DLQ will assist you to dosen't lost an event that fail for some reason. So if somehow the task fails, raising any kind of exception, the event will be sent to DLQ and after some delay defined by `rabbit-client` strategy it will be back in the main queue so that the application can try to process it again.

- [When and how to use the RabbitMQ Dead Letter Exchange](https://www.cloudamqp.com/blog/when-and-how-to-use-the-rabbitmq-dead-letter-exchange.html)

## **How optimize concurrent jobs?**

Just increase the value of `concurrent` attribute in the Subscribe.

However if the job consists in [CPU bound](https://en.wikipedia.org/wiki/CPU-bound) or long running tasks workloads it's a good choice decrease the value.

- [How to Optimize the RabbitMQ Prefetch Count](https://www.cloudamqp.com/blog/how-to-optimize-the-rabbitmq-prefetch-count.html)


## **Why use publisher-confirms?**

The RabbitMQ documentation are a great place, so I don't repeat myself =)

Check this links:

- [Consumer Acknowledgements and Publisher Confirms ](https://www.rabbitmq.com/confirms.html#publisher-confirms)
- [Introducing Publisher Confirms](https://blog.rabbitmq.com/posts/2011/02/introducing-publisher-confirms)
