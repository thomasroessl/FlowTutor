pipeline {
    agent { docker { image 'python:3.10.7-alpine' } }
    stages {
        stage('dependencies') {
            steps {
                sh 'python -m venv venv'
                sh 'source ./venv/bin/activate'
                sh 'python -m pip install -r requirements_dev.txt'
                sh 'python -m pip install -r requirements.txt'
            }
        }
    }
}
