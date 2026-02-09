pipeline {
  agent any

  environment {
    DOCKERHUB_CREDS = 'dockerhub-creds'     // Jenkins credentials ID
    IMAGE_NAME      = 'DOCKERHUB_USERNAME/REPO_NAME'
    IMAGE_TAG       = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        sh """
          docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
          docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
        """
      }
    }

    stage('Login & Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDS, usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
          sh """
            echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE_NAME}:${IMAGE_TAG}
            docker push ${IMAGE_NAME}:latest
            docker logout
          """
        }
      }
    }
  }

  post {
    always {
      sh "docker images | head -n 20 || true"
    }
  }
}
