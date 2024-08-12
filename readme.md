

# build

1. Set your Google Cloud project:
```sh
  gcloud config set project <YOUR_PROJECT_ID> 
  ```

2. Build your Docker image:
```sh
docker build -t <REGION>-docker.pkg.dev/<YOUR_PROJECT_ID>/<REPOSITORY_NAME>/<IMAGE_NAME>:<TAG> .
```

3. Push the Docker image to Google Container Registry:
```sh
docker push <REGION>-docker.pkg.dev/<YOUR_PROJECT_ID>/<REPOSITORY_NAME>/<IMAGE_NAME>:<TAG>
```

4. Deploy your image to Google Cloud Run:
```sh
gcloud run deploy <SERVICE_NAME> --image=<REGION>-docker.pkg.dev/<YOUR_PROJECT_ID>/<REPOSITORY_NAME>/<IMAGE_NAME>:<TAG> --platform managed --region <REGION> --allow-unauthenticated
```
