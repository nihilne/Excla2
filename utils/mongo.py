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

log = logging.getLogger(__name__)


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
        if self.client is None:
            raise RuntimeError("Client doesn't exist, cannot close connection.")

        await self.client.close()
        log.info("Connection to MongoDB client closed.")

    async def ping(self):
        if self.client is None:
            raise RuntimeError("Client doesn't exist, cannot ping.")

        ping = await self.client.admin.command("ping")
        log.info(f"Pinged MongoDB database with response {ping}.")


uri = os.getenv("MONGODB_URI")
if not uri:
    raise ValueError("MongoDB URI not found as environment variable.")

cert_files = glob("./certs/X509-cert*.pem")
if not cert_files:
    raise ValueError("No X509 certificate found.")
if len(cert_files) > 1:
    raise ValueError("More than one certificate files found.")


db = MongoDB(uri, cert)
