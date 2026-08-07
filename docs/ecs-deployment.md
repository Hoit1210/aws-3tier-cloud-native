# ECS Fargate Deployment Notes

This project was evolved from an EC2-hosted Docker Compose environment to an AWS-managed container runtime using ECR and ECS Fargate.

## Deployment flow

```text
Local/EC2 Docker Image
        ↓
Amazon ECR
        ↓
ECS Task Definition
        ↓
ECS Service
        ↓
Fargate Task
        ↓
Application :5000
```

## ECR login

Use an IAM role attached to the EC2 instance instead of embedding long-lived AWS access keys in the application.

```bash
aws ecr get-login-password --region ap-northeast-2 \
  | docker login --username AWS --password-stdin \
    <AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com
```

## Image push

```bash
docker build -t weather-app ./backend

docker tag weather-app:latest \
  <AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/weather-app:latest

docker push \
  <AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/weather-app:latest
```

## ECS configuration used in the project

- Launch type: AWS Fargate
- Task family: `weather-task`
- Container name: `app`
- Container port: `5000`
- Desired task count: `1`
- Image source: Amazon ECR private repository
- Public IP: enabled during the project verification stage
- Load balancer: not used during the direct endpoint verification stage

## Portfolio note

The project verified ECS Service/Task execution and direct application access. High availability, Auto Scaling, load balancing, and production-grade TLS termination were not part of this project scope.
