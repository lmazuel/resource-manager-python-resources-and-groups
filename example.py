import os
import json
from azure.common.credentials import ServicePrincipalCredentials
import azure.mgmt.resource.resources

WEST_US = 'westus'
GROUP_NAME = 'azure-sample-group'

# Manage resources and resource groups - create, update and delete a resource group,
# deploy a solution into a resource group, export an ARM template. Create, read, update
# and delete a resource
#
# This script expects that the following environment vars are set:
#
# AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
# AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
# AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret
# AZURE_SUBSCRIPTION_ID: with your Azure Subscription Id
#
def run_example():
    """Resource Group management example."""
    #
    # Create the Resource Manager Client with an Application (service principal) token provider
    #
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )

    # Next line load "latest" => 2016-07-01
    #client = azure.mgmt.resource.resources.client(credentials=credentials)

    os.environ['AZURE_RESOURCE_RESOURCES_API_VERSION'] = '2016-02-01'
    # Now load '2016-02-01'
    client = azure.mgmt.resource.resources.client(credentials=credentials)

    # Explicitly load '2016-02-01'
    #client = azure.mgmt.resource.resources.client(api_version='2016-02-01', credentials=credentials)

    #
    # Managing resource groups
    #
    resource_group_params = {'location':'westus'}

    # List Resource Groups
    print('List Resource Groups')
    for item in client.resource_groups.list():
        print_item(item)

    # Create Resource group
    print('Create Resource Group')
    print_item(client.resource_groups.create_or_update(GROUP_NAME, resource_group_params))

    # Modify the Resource group
    print('Modify Resource Group')
    resource_group_params.update(tags={'hello': 'world'})
    print_item(client.resource_groups.create_or_update('azure-sample-group', resource_group_params))

    # Create a Key Vault in the Resource Group
    print('Create a Key Vault via a Generic Resource Put')
    key_vault_params = {
        'location': 'westus',
        'properties':  {
            'sku': {'family': 'A', 'name': 'standard'},
            'tenantId': os.environ['AZURE_TENANT_ID'],
            'accessPolicies': [],
            'enabledForDeployment': True,
            'enabledForTemplateDeployment': True,
            'enabledForDiskEncryption': True
        }
    }
    client.resources.create_or_update(GROUP_NAME,
                                      'Microsoft.KeyVault',
                                      '',
                                      'vaults',
                                      'azureSampleVault',
                                      '2015-06-01',
                                      key_vault_params)

    # List Resources within the group
    print('List all of the resources within the group')
    for item in client.resource_groups.list_resources(GROUP_NAME):
        print_item(item)

    # Export the Resource group template
    print('Export Resource Group Template')
    print(json.dumps(client.resource_groups.export_template(GROUP_NAME, ['*']).template, indent=4))
    print('\n\n')

    # Delete Resource group and everything in it
    print('Delete Resource Group')
    delete_async_operation = client.resource_groups.delete(GROUP_NAME)
    delete_async_operation.wait()
    print("\nDeleted: {}".format(GROUP_NAME))

def print_item(group):
    """Print a ResourceGroup instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    print("\tLocation: {}".format(group.location))
    print("\tTags: {}".format(group.tags))
    print_properties(group.properties)

def print_properties(props):
    """Print a ResourceGroup propertyies instance."""
    if props and props.provisioning_state:
        print("\tProperties:")
        print("\t\tProvisioning State: {}".format(props.provisioning_state))
    print("\n\n")

if __name__ == "__main__":
    run_example()
