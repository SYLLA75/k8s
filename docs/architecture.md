# Architecture

```mermaid
graph LR
  UI[Flask UI] -- ansible_runner --> ANS(Ansible)
  ANS -- SSH --> Nodes((Kubernetes Nodes))
  DB[(SQLite)] -- stores --> UI
```
