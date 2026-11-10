# Mutillidae — the OWASP Mutillidae II deliberately vulnerable web app. This
# image bundles Apache+PHP+MySQL in one container so it fits the lab's
# single-container-per-challenge model. We alias the maintainer's image locally
# as localhost/lab/mutillidae:latest; pin by digest at deploy time via
# scripts/image-pins.py.
FROM vulfocus/mutillidae:latest

# Mutillidae serves on port 80 inside the container (published 8083 in the lab).
EXPOSE 80
