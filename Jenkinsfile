pipeline {
    agent { docker { image 'python:3.10.7-alpine' } }
    stages {
        stage('dependencies') {
            steps {
                withPythonEnv('python') {
                sh 'python -m pip install -r requirements_dev.txt'
                sh 'python -m pip install -r requirements.txt'
                }
            }
        }
    }
}