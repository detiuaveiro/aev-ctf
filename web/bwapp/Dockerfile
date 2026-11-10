# bWAPP — "buggy Web APPlication", an intentionally vulnerable PHP web app
# (OWASP bWAPP project). This image bundles Apache+PHP+MySQL in one container so
# it fits the lab's single-container-per-challenge model. We alias the
# maintainer's image locally as localhost/lab/bwapp:latest; pin by digest at
# deploy time via scripts/image-pins.py.
FROM raesene/bwapp:latest

# bWAPP serves on port 80 inside the container (published 8081 in the lab).
EXPOSE 80
