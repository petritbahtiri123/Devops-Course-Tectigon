pipeline {
  agent any

  environment {
    DOCKERHUB_CREDS = 'dockerhub-creds'
    DOCKERHUB_USER  = 'petritbahtiri123'
    IMAGE_REPO      = 'devops-course-tectigon'   // emri i repo në Docker Hub
    IMAGE_NAME      = "${DOCKERHUB_USER}/${IMAGE_REPO}"
    IMAGE_TAG       = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build') {
      steps {
        sh """
          set -e
          docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
          docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
        """
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDS, usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
          sh """
            set -e
            echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE_NAME}:${IMAGE_TAG}
            docker push ${IMAGE_NAME}:latest
            docker logout
          """
        }
      }
    }
  }
}
