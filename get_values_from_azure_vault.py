import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName = 'prasanna-azure-vault'
KVUri = f"https://{keyVaultName}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

devschuser = client.get_secret('dev-sch-user')
devschpassword = client.get_secret('dev-sch-password1')
devschurl = client.get_secret('dev-sch-url')
qaschuser = client.get_secret('qa-sch-user')
qaschpassword = client.get_secret('qa-sch-password')
qaschurl = client.get_secret('qa-sch-url')

print ('##vso[task.setvariable variable=DEV_SCH_USER]'+devschuser.value)
print ('##vso[task.setvariable variable=DEV_SCH_PASSWORD]'+devschpassword.value)
print ('##vso[task.setvariable variable=DEV_SCH_URL]'+devschurl.value)

print ('##vso[task.setvariable variable=QA_SCH_USER]'+qaschuser.value)
print ('##vso[task.setvariable variable=QA_SCH_PASSWORD]'+qaschpassword.value)
print ('##vso[task.setvariable variable=QA_SCH_URL]'+qaschurl.value)

