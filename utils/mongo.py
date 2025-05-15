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


class MongoDB:
    def __init__(
        self,
        uri: str,
        x509_cert: str,
    ):
        self.log = logging.getLogger(__name__)
        self.uri = uri
        self.x509_cert = x509_cert

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
        self.log.info("Set up MongoDB client and db successfully")

    async def close(self) -> None:
        if self.client:
            await self.client.close()
            self.log.info("MongoDB connection closed successfully")
        else:
            self.log.warning("Could not close connection: No client found")

    async def ping(self):
        if self.client:
            ping = await self.client.admin.command("ping")
            self.log.info(f"Pinged MongoDB database with response {ping}")
        else:
            self.log.warning("Could not ping: No client found")


db = MongoDB(uri, cert)
