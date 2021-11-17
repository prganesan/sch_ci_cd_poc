import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName = 'prasanna-azure-vault'
KVUri = f"https://{keyVaultName}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

dev-sch-user=client.get_secret('dev-sch-user')
dev-sch-password=client.get_secret('dev-sch-password')
dev-sch-url=client.get_secret('dev-sch-url')
dev-sch-password=client.get_secret('dev-sch-password')
qa-sch-user=client.get_secret('qa-sch-user')
qa-sch-password=client.get_secret('qa-sch-password')
qa-sch-url=client.get_secret('qa-sch-url')

print ('##vso[task.setvariable variable=DEV_SCH_USER]'+dev-sch-user)
print ('##vso[task.setvariable variable=DEV_SCH_PASSWORD]'+dev-sch-password)
print ('##vso[task.setvariable variable=DEV_SCH_URL]'+dev-sch-url)

print ('##vso[task.setvariable variable=QA_SCH_USER]'+qa-sch-user)
print ('##vso[task.setvariable variable=QA_SCH_PASSWORD]'+qa-sch-password)
print ('##vso[task.setvariable variable=QA_SCH_URL]'+qa-sch-url)

