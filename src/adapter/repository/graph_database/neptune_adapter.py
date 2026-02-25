import os
import re
import json
import traceback
from typing import Any, List, Dict

import boto3
from botocore.config import Config as BotoConfig

from src.core.ports.graph_database_port import GraphDatabasePort


class NeptuneDatabaseAdapter(GraphDatabasePort):
    """Concrete adapter for Amazon Neptune using openCypher via boto3.

    Uses the `neptunedata` boto3 client to execute openCypher queries against
    a Neptune cluster. Connection management (boto3 client lifecycle) is handled
    internally — consistent with the port's encapsulation principle.

    Required environment variables (or constructor params):
        - NEPTUNE_ENDPOINT: The Neptune cluster endpoint (e.g., https://your-cluster.region.neptune.amazonaws.com:8182)
        - AWS_REGION: The AWS region (e.g., us-east-1)
        - AWS_ACCESS_KEY_ID: (optional if using IAM role / instance profile)
        - AWS_SECRET_ACCESS_KEY: (optional if using IAM role / instance profile)
    """

    def __init__(
        self,
        neptune_endpoint: str = None,
        aws_region: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
    ):
        self._neptune_endpoint = neptune_endpoint or os.getenv("NEPTUNE_ENDPOINT")
        self._aws_region = aws_region or os.getenv("AWS_REGION", "us-east-1")
        self._aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self._aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")

        self._client = None

    # ──────────────────────────────────────────────
    # Internal: connection management
    # ──────────────────────────────────────────────

    def _get_client(self):
        """Lazy-initialize and return the boto3 neptunedata client.
        Creates the client on first call, reuses it on subsequent calls.
        This is an internal detail — not part of the public port contract.
        """
        if self._client is None:
            if not self._neptune_endpoint:
                raise ValueError(
                    "Neptune configuration missing (NEPTUNE_ENDPOINT)"
                )

            print("Initializing Neptune boto3 client")

            client_kwargs = {
                "service_name": "neptunedata",
                "region_name": self._aws_region,
                "endpoint_url": self._neptune_endpoint,
                "config": BotoConfig(
                    retries={"max_attempts": 3, "mode": "adaptive"}
                ),
            }

            # Support both explicit credentials and IAM role / instance profile
            if self._aws_access_key_id and self._aws_secret_access_key:
                client_kwargs["aws_access_key_id"] = self._aws_access_key_id
                client_kwargs["aws_secret_access_key"] = self._aws_secret_access_key

            self._client = boto3.client(**client_kwargs)
            print("Neptune client initialized successfully")

        return self._client

    # ──────────────────────────────────────────────
    # Write-query guard (shared concern — see observations)
    # ──────────────────────────────────────────────

    def _is_write_query(self, query: str) -> bool:
        """Detect write operations in Cypher queries."""
        return re.search(
            r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE
        ) is not None

    # ──────────────────────────────────────────────
    # Port contract: execute_query
    # ──────────────────────────────────────────────

    def execute_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> List[Dict[str, Any]]:
        if self._is_write_query(query):
            raise ValueError("Write Queries are not supported in this agent")
        try:
            client = self._get_client()

            # Neptune openCypher API expects parameters as a JSON string
            request_kwargs = {"openCypherQuery": query}
            if params:
                request_kwargs["parameters"] = json.dumps(params)

            response = client.execute_open_cypher_query(**request_kwargs)

            # Neptune returns results in response["results"]
            results = response.get("results", [])

            # Neptune already returns plain dicts (no custom date types like Neo4j),
            # so no serializer is needed — the data is already JSON-compatible.
            return results

        except Exception as e:
            print(f"Error executing Neptune query: {e}")
            traceback.print_exc()
            raise e

    # ──────────────────────────────────────────────
    # Port contract: get_schema
    # ──────────────────────────────────────────────

    def get_schema(self) -> List[Dict[str, Any]]:
        """Retrieve schema information from Neptune.

        Neptune does NOT have a built-in equivalent to Neo4j's apoc.meta.data().
        We use Neptune's RDF/property-graph summary API and supplement with
        openCypher introspection queries to approximate the schema.

        NOTE: This highlights a port design observation — see analysis below.
        """
        try:
            # Strategy: use openCypher introspection to discover labels & properties
            # Step 1: Get all node labels
            labels_query = "MATCH (n) RETURN DISTINCT labels(n) AS labels"
            labels_result = self.execute_query(labels_query)

            schema = []

            for row in labels_result:
                node_labels = row.get("labels", [])
                if not node_labels:
                    continue

                label = node_labels[0] if isinstance(node_labels, list) else node_labels

                # Step 2: Get properties for this label
                props_query = (
                    f"MATCH (n:`{label}`) "
                    f"WITH keys(n) AS ks UNWIND ks AS k "
                    f"RETURN DISTINCT k AS property"
                )
                props_result = self.execute_query(props_query)
                attributes = {
                    r["property"]: "STRING"  # Neptune doesn't expose property types easily
                    for r in props_result
                }

                # Step 3: Get relationships from this label
                rels_query = (
                    f"MATCH (n:`{label}`)-[r]->(m) "
                    f"RETURN DISTINCT type(r) AS rel_type, head(labels(m)) AS target_label"
                )
                rels_result = self.execute_query(rels_query)
                relationships = {
                    r["rel_type"]: r.get("target_label", "Unknown")
                    for r in rels_result
                }

                schema.append({
                    "label": label,
                    "attributes": attributes,
                    "relationships": relationships,
                })

            return schema

        except Exception as e:
            print(f"Error retrieving Neptune schema: {e}")
            traceback.print_exc()
            raise e

    # ──────────────────────────────────────────────
    # Port contract: cleanup
    # ──────────────────────────────────────────────

    def cleanup(self):
        """Clean up the boto3 client resources."""
        if self._client is not None:
            # boto3 clients don't have an explicit close(),
            # but we nullify the reference for consistency and GC.
            self._client = None
            print("Neptune client cleaned up")
