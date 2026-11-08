$service = kubectl get svc eks-cicd-service `
    -o jsonpath="{.status.loadBalancer.ingress[0].hostname}"

if (-not $service) {

    Write-Host "Load balancer not ready"

    exit 1

}

$url = "http://$service/health"

Write-Host "Testing: $url"

$response = Invoke-WebRequest `
    -Uri $url `
    -UseBasicParsing


if ($response.StatusCode -ne 200) {

    Write-Error "Smoke test failed"

    exit 1

}


Write-Host "Smoke test passed"