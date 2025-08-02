pipeline {
    agent any

    environment {
        FUNCTION_NAME = 'iit_cc_dataextract_etl'
        REGION = 'us-east-1'
        ZIP_FILE = 'python.zip'
    }

    stages {
        stage('Setup Virtual Environment') {
            steps {
                sh '''
                echo "✅ Creating Python virtual environment..."
                python3 -m venv venv
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                echo "✅ Activating virtual environment and installing dependencies..."
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Package Lambda Function') {
            steps {
                sh '''
                echo "✅ Packaging application into zip file for AWS Lambda..."
                zip -r ${ZIP_FILE} app/
                ls -lh
                '''
            }
        }

        stage('Deploy to AWS Lambda') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'aws-access-key-id', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                    echo "✅ Deploying to AWS Lambda..."

                    aws lambda update-function-code \
                      --function-name ${FUNCTION_NAME} \
                      --region us-east-1 \
                      --zip-file fileb://${ZIP_FILE}
                    '''
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up...'
            sh 'rm -rf venv'
        }
    }
}

