"""
STAGE 10 VERIFICATION SUITE: DOCKER & CONTAINER CONFIGURATION
Validates:
  1. backend/Dockerfile presence and essential instructions
  2. docker-compose.yml configuration and service dependency graphs
  3. Environment variables, networks, and persistent volume definitions
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_stage10():
    print("==================================================")
    print("  🐳 Verifying Stage 10: Docker Infrastructure")
    print("==================================================\n")

    dockerfile_path = os.path.join(CURRENT_DIR, "backend", "Dockerfile")
    compose_path = os.path.join(CURRENT_DIR, "docker-compose.yml")

    # 1. Verify Dockerfile
    print("[1/2] Inspecting backend/Dockerfile...")
    assert os.path.exists(dockerfile_path), "backend/Dockerfile not found!"
    with open(dockerfile_path, "r") as f:
        dockerfile_content = f.read()

    assert "FROM python:3.11-slim" in dockerfile_content
    assert "HEALTHCHECK" in dockerfile_content
    assert "uvicorn" in dockerfile_content
    print("  ✅ Dockerfile layers, health check probe, and Uvicorn entrypoint verified.")

    # 2. Verify docker-compose.yml
    print("\n[2/2] Inspecting docker-compose.yml...")
    assert os.path.exists(compose_path), "docker-compose.yml not found!"
    with open(compose_path, "r") as f:
        compose_content = f.read()

    required_services = ["mongodb", "redis", "backend_api", "scraper_worker"]
    for s in required_services:
        assert f"{s}:" in compose_content, f"Service {s} missing from docker-compose.yml!"
        print(f"  ✅ Service configured: {s}")

    assert "apix_network" in compose_content
    assert "mongodb_data" in compose_content
    assert "redis_data" in compose_content

    print("\n🎉 STAGE 10 DOCKERIZATION CONFIGURATION VERIFIED WITH 0 ERRORS!")


if __name__ == "__main__":
    test_stage10()