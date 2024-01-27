#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

def get_toxic(url, proxy_name, toxic_name):
    response = requests.get(f"{url}/proxies/{proxy_name}/toxics/{toxic_name}")
    if response.status_code == 200:
        return True, response.json()
    elif response.status_code == 404:
        return False, None
    response.raise_for_status()

def create_toxic(module, url, proxy_name, toxic_type, toxic_name, attributes):
    exists, _ = get_toxic(url, proxy_name, toxic_name)
    if exists:
        module.exit_json(changed=False, msg="Toxic already exists")

    data = {
        "type": toxic_type,
        "name": toxic_name,
        "attributes": attributes
    }
    response = requests.post(f"{url}/proxies/{proxy_name}/toxics", json=data)
    if response.status_code == 201:
        return True, response.json()
    module.fail_json(msg="Failed to create toxic", details=response.text)

def delete_toxic(module, url, proxy_name, toxic_name):
    exists, _ = get_toxic(url, proxy_name, toxic_name)
    if not exists:
        module.exit_json(changed=False, msg="Toxic does not exist")

    response = requests.delete(f"{url}/proxies/{proxy_name}/toxics/{toxic_name}")
    if response.status_code == 204:
        return True, None
    module.fail_json(msg="Failed to delete toxic", details=response.text)

def main():
    argument_spec = dict(
        url=dict(type='str', required=True),
        proxy_name=dict(type='str', required=True),
        toxic_type=dict(type='str', required=True),
        toxic_name=dict(type='str', required=True),
        attributes=dict(type='dict', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    url = module.params['url']
    proxy_name = module.params['proxy_name']
    toxic_type = module.params['toxic_type']
    toxic_name = module.params['toxic_name']
    attributes = module.params['attributes']
    state = module.params['state']

    if module.check_mode:
        module.exit_json(changed=False)

    if state == 'present':
        changed, result = create_toxic(module, url, proxy_name, toxic_type, toxic_name, attributes)
    else:  # state == 'absent'
        changed, result = delete_toxic(module, url, proxy_name, toxic_name)

    module.exit_json(changed=changed, toxic=result)

if __name__ == '__main__':
    main()
