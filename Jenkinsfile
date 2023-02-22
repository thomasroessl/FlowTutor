pipeline {
    agent { docker { image 'python:3.10.7-alpine' } }
    stages {
        stage('dependencies') {
            steps {
                sh 'python -m pip install -r requirements_dev.txt --user'
                sh 'python -m pip install -r requirements.txt --user'
            }
        }
    }
}