"""
utils/mongo.py
---
Author: Enitoxy
Co-authors: [empty]
License: GPL-3.0
Description: A utility that connects to a MongoDB database
"""

import logging
import os
from glob import glob

from pymongo import AsyncMongoClient

uri = os.getenv("MONGODB_URI")
cert = glob("./certs/X509-cert*.pem")[0]

log = logging.getLogger(__name__)


if not uri:
    log.error("URI not found as environment variable, exiting...")
    exit()


class MongoDB:
    def __init__(
        self,
        uri: str,
        x509_cert: str,
    ):
        self.client = None
        self.db = None
        self.uri = uri
        self.x509_cert = x509_cert

    async def connect(self) -> None:
        self.client = AsyncMongoClient(
            self.uri,
            authSource="$external",
            authMechanism="MONGODB-X509",
            retryWrites=True,
            w="majority",
            tls=True,
            tlsCertificateKeyFile=self.x509_cert,
        )
        self.db = self.client["excla2"]
        log.info("Connected to MongoDB client.")

    async def close(self) -> None:
        if self.client:
            await self.client.close()
            log.info("Connection to MongoDB client closed.")
        else:
            log.warning("Could not close connection: No client found.")

    async def ping(self):
        if self.client:
            ping = await self.client.admin.command("ping")
            log.info(f"Pinged MongoDB database with response {ping}.")
        else:
            log.warning("Could not ping: No client found.")


db = MongoDB(uri, cert)
