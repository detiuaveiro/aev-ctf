# OWASP Juice Shop — the canonical insecure Node.js web app. We do not rebuild
# it from source here (an npm build would need the whole toolchain + registry);
# we alias the maintainer's published image so the lab builds it locally as
# localhost/lab/juiceshop:latest. Pin the base by digest at deploy time via
# scripts/image-pins.py (see images.lock.json).
FROM bkimminich/juice-shop:latest

# Juice Shop serves on 3000 by default; the flag is injected by the helper as
# the FLAG env var and consumed by the app's challenge logic.
EXPOSE 3000
