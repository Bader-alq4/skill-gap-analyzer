@description('Location for all resources')
param location string = resourceGroup().location

@description('Name prefix for all resources')
param baseName string = 'skillgapanalyzer'

// Registry, plan, and app names
var registryName = toLower('${baseName}acr')
var planName     = '${baseName}-plan'
var webAppName   = '${baseName}-app'

// 1) Azure Container Registry (Basic SKU)
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: registryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// 2) App Service Plan (Free tier, Linux)
resource plan 'Microsoft.Web/serverfarms@2021-02-01' = {
  name: planName
  location: location
  sku: {
    name: 'F1'
    tier: 'Free'
  }
  properties: {
    // reserved = true makes this a Linux plan
    reserved: true
  }
}

// 3) Web App (Linux container)
resource webapp 'Microsoft.Web/sites@2021-02-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      // Specify the Docker image to run
      linuxFxVersion: 'DOCKER|${registryName}.azurecr.io/skill-gap-backend:latest'
      // Use managed identity to pull from ACR
      acrUseManagedIdentityCreds: true
      // Additional app settings
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
      ]
    }
  }
  dependsOn: [acr]
}

// 4) App Service Plan for frontend (Free Linux)
resource fePlan 'Microsoft.Web/serverfarms@2021-02-01' = {
  name: '${baseName}-fe-plan'
  location: location
  sku: { name: 'F1'; tier: 'Free' }
  properties: { reserved: true }      // Linux
}

// 5) Web App for frontend (Linux container)
resource feApp 'Microsoft.Web/sites@2021-02-01' = {
  name: '${baseName}-fe-app'
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: fePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${registryName}.azurecr.io/skill-gapanalyzer-frontend:latest'
      acrUseManagedIdentityCreds: true
      appSettings: [
        { name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'; value: 'false' }
      ]
    }
  }
  dependsOn: [
    acr       // ensure your registry exists first
    fePlan    // and the plan exists before the app
  ]
}
