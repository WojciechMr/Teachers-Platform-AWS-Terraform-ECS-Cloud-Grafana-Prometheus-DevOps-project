Teachers Platform — DevOps Project 

Opis projektu

Projekt "Teachers Platform" to kompleksowe rozwiązanie DevOps, które integruje różnorodne technologie chmurowe i narzędzia automatyzacji w celu stworzenia skalowalnej i monitorowanej aplikacji edukacyjnej. Platforma została zaprojektowana z myślą o nauczycielach i studentach, oferując funkcjonalności takie jak zarządzanie kursami, ocenami i komunikacją.

☁️ Technologie i narzędzia

AWS (Amazon Web Services): wykorzystanie usług chmurowych do hostingu aplikacji i baz danych.

Terraform: infrastruktura jako kod (IaC) do automatycznego provisioningu zasobów AWS.

Docker & ECS (Elastic Container Service): konteneryzacja aplikacji i ich orkiestracja w chmurze.

Prometheus & Grafana: monitorowanie aplikacji i infrastruktury z zaawansowanymi dashboardami.

Django: framework webowy w Pythonie do budowy aplikacji backendowej.

CI/CD: automatyzacja procesów budowania, testowania i wdrażania aplikacji.

Struktura repozytorium :

/teachers-platform
├── /terraform           # Skrypty Terraform do provisioningu infrastruktury
├── /docker              # Dockerfile i konfiguracje kontenerów
├── /django              # Aplikacja Django
├── /monitoring          # Konfiguracje Prometheus i Grafana
├── README.md            # Dokumentacja projektu
└── .gitignore           # Ignorowane pliki i katalogi

🚀 Szybki start

1. Zainstaluj Terraform i AWS CLI:
2. Skonfiguruj AWS CLI:
aws configure
3. Zainicjuj Terraform:
cd terraform
terraform init
4. Zastosuj konfigurację:
terraform apply
5. Zbuduj i uruchom kontenery:
cd docker
docker-compose up --build
6. Dostęp do aplikacji:
Frontend: http://localhost:8000
Grafana: http://localhost:3000
Prometheus: http://localhost:9090

📊 Monitorowanie

Prometheus zbiera metryki z aplikacji i infrastruktury.

Grafana wyświetla interaktywne dashboardy z danymi z Prometheus.

🔐 Bezpieczeństwo

Dane wrażliwe, takie jak hasła i klucze API, są przechowywane w pliku .env i są ignorowane przez Git dzięki wpisom w .gitignore.

📄 Licencja

Projekt jest dostępny na licencji MIT.