# Kubernetes Ansible GUI

Ce projet permet de deployer un cluster Kubernetes multi-noeuds via une interface web.

## Prerequis
- Docker et Docker Compose
- Acces SSH aux noeuds (Ubuntu 22.04, Debian 12 ou RHEL 9)
  
Le conteneur d'execution installe maintenant `openssh-client` afin que
les playbooks Ansible puissent se connecter aux hôtes.

## Demarrage rapide
1. Copier `.env.example` vers `.env` et ajuster les identifiants.
2. Executer `./bootstrap.sh`.
3. Ouvrir `http://localhost:5000` et se connecter.
4. Creer un cluster dans l'UI puis cliquer **Deploy**.

## Makefile
- `make up` lance l'application en arriere-plan.
- `make down` arrete les conteneurs.
- `make lint` execute ansible-lint et flake8.

## CLI (optionnel)
Il est possible d'executer les playbooks manuellement avec `ansible-playbook` dans le repertoire `ansible/`.
