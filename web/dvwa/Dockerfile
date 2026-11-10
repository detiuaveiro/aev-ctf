# DVWA — Damn Vulnerable Web Application, a PHP/MySQL web app. This image
# bundles Apache+PHP+MySQL in one container so it fits the lab's
# single-container-per-challenge model. We alias the maintainer's image locally
# as localhost/lab/dvwa:latest; pin by digest at deploy time via
# scripts/image-pins.py.
FROM vulnerables/web-dvwa:latest

# DVWA serves on port 80 inside the container (published 8082 in the lab).
EXPOSE 80
