import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName = 'prasanna-azure-vault'
KVUri = f"https://{keyVaultName}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

dev-sch-user=client.get_secret('dev-sch-user')
dev-sch-password=client.get_secret('dev-sch-password')
qa-sch-user=client.get_secret('qa-sch-user')
qa-sch-password=client.get_secret('qa-sch-password')

print ('##vso[task.setvariable variable=dev-sch-user]'+dev-sch-user)
print ('##vso[task.setvariable variable=dev-sch-password]'+dev-sch-password)
print ('##vso[task.setvariable variable=qa-sch-user]'+qa-sch-user)
print ('##vso[task.setvariable variable=qa-sch-password]'+qa-sch-password)
