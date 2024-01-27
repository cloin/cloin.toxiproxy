#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

def get_proxy(url, name):
    response = requests.get(f"{url}/proxies/{name}")
    if response.status_code == 200:
        return True, response.json()
    elif response.status_code == 404:
        return False, None
    response.raise_for_status()

def create_proxy(module, url, name, listen, upstream):
    exists, _ = get_proxy(url, name)
    if exists:
        module.exit_json(changed=False, msg="Proxy already exists")
    
    data = {
        "name": name,
        "listen": listen,
        "upstream": upstream,
        "enabled": True
    }
    response = requests.post(f"{url}/proxies", json=data)
    if response.status_code == 201:
        return True, response.json()
    module.fail_json(msg="Failed to create proxy", details=response.text)

def delete_proxy(module, url, name):
    exists, _ = get_proxy(url, name)
    if not exists:
        module.exit_json(changed=False, msg="Proxy does not exist")
    
    response = requests.delete(f"{url}/proxies/{name}")
    if response.status_code == 204:
        return True, None
    module.fail_json(msg="Failed to delete proxy", details=response.text)

def main():
    argument_spec = dict(
        url=dict(type='str', required=True),
        name=dict(type='str', required=True),
        listen=dict(type='str', required=True),
        upstream=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    url = module.params['url']
    name = module.params['name']
    listen = module.params['listen']
    upstream = module.params['upstream']
    state = module.params['state']

    if module.check_mode:
        module.exit_json(changed=False)

    if state == 'present':
        changed, result = create_proxy(module, url, name, listen, upstream)
    else:  # state == 'absent'
        changed, result = delete_proxy(module, url, name)

    module.exit_json(changed=changed, proxy=result)

if __name__ == '__main__':
    main()
