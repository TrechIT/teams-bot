#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os


class DefaultConfig:
    """Bot Configuration"""

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    CHROMA_HOST_IP = os.environ.get("CHROMA_HOST_IP, ")
    CHROMA_HOST_PORT = os.environ.get("CHROMA_HOST_PORT", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    CHROMA_COLLECTION_NAME = "halo_knowledge_base"
    HALO_BASE_URL = os.environ.get("HALO_BASE_URL")
    HALO_CLIENT_ID = os.environ.get("HALO_CLIENT_ID")
    HALO_CLIENT_SECRET = os.environ.get("HALO_CLIENT_SECRET")
