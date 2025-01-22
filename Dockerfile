ARG PYTHON_VERSION=3.11

FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip && yum install -y git

# Install dependencies into the virtual environment
COPY requirements.txt .
RUN pip install -r requirements.txt

# Precompile python files for faster startup
RUN python -m compileall -q .

# Copy the function code
COPY src ./src

COPY index.py .

COPY index_test.py .

# Set the Lambda function handler
CMD ["index.handler"]