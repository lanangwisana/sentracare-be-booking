# sentracare-be-booking/rabbitmq.py
import aio_pika
import os
import json

# RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
# RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
# RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# async def publish_booking_confirmed(payload: dict):
#     connection = await aio_pika.connect_robust(
#         f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"
#     )
#     async with connection:
#         channel = await connection.channel()
#         exchange = await channel.declare_exchange("booking", aio_pika.ExchangeType.TOPIC)
#         message = aio_pika.Message(
#             body=json.dumps(payload).encode(),
#             content_type="application/json"
#         )
#         await exchange.publish(message, routing_key="booking.confirmed")
#         print(f"Published booking.confirmed event for booking_id={payload['booking_id']}")