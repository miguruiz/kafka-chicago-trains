"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

logger = logging.getLogger(__name__)


class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas


        self.broker_properties = {
            'bootstrap.servers': 'localhost:9092',
            'allow.auto.create.topics': False
        }

        self.client = AdminClient(self.broker_properties)

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        self.producer = AvroProducer( {"bootstrap.servers": self.broker_properties["bootstrap.servers"], 'schema.registry.url': 'http://localhost:8081'})

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        self.client.create_topics(
            [
                NewTopic(
                    topic=self.topic_name,
                    num_partitions=1,
                    replication_factor=1,
                    config={
                        "cleanup.policy": "delete",
                        "compression.type": "lz4",
                        "delete.retention.ms": "2000",
                        "file.delete.delay.ms": "2000",
                    },
                )
            ]
        )

        logger.info(f"Created topic: {self.topic_name}")

    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        self.producer.flush()
        self.producer.close()

        logger.info(f"Closing producer to topic {self.topic_name} ")

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
