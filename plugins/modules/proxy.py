#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

def get_proxy(url, name):
    """Retrieve the proxy configuration."""
    response = requests.get(f"{url}/proxies/{name}")
    if response.status_code == 200:
        return True, response.json()
    elif response.status_code == 404:
        return False, None
    response.raise_for_status()

def create_or_update_proxy(module, url, name, listen, upstream, enabled):
    """Create or update a proxy."""
    exists, current_proxy = get_proxy(url, name)
    if exists:
        # Update the proxy if 'enabled' state is provided and different from current state.
        if 'enabled' in module.params and current_proxy['enabled'] != enabled:
            data = {"enabled": enabled}
            if listen and upstream:
                data.update({"listen": listen, "upstream": upstream})
            response = requests.post(f"{url}/proxies/{name}", json=data)
            if response.status_code == 200:
                return True, response.json()
            else:
                module.fail_json(msg="Failed to update proxy", details=response.text)
        # No changes needed if the proxy exists and no update is required.
        module.exit_json(changed=False, proxy=current_proxy)
    else:
        # Create a new proxy if it doesn't exist.
        data = {
            "name": name,
            "listen": listen,
            "upstream": upstream,
            "enabled": enabled
        }
        response = requests.post(f"{url}/proxies", json=data)
        if response.status_code == 201:
            return True, response.json()
        else:
            module.fail_json(msg="Failed to create proxy", details=response.text)

def delete_proxy(module, url, name):
    """Delete an existing proxy."""
    exists, _ = get_proxy(url, name)
    if not exists:
        module.exit_json(changed=False, msg="Proxy does not exist")
    
    response = requests.delete(f"{url}/proxies/{name}")
    if response.status_code == 204:
        return True, None
    else:
        module.fail_json(msg="Failed to delete proxy", details=response.text)

def main():
    argument_spec = dict(
        url=dict(type='str', required=True),
        name=dict(type='str', required=True),
        listen=dict(type='str', required=False, default=None),
        upstream=dict(type='str', required=False, default=None),
        enabled=dict(type='bool', required=False, default=True),
        state=dict(type='str', default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[('state', 'present', ['name'])]
    )

    url = module.params['url']
    name = module.params['name']
    listen = module.params['listen']
    upstream = module.params['upstream']
    enabled = module.params['enabled']
    state = module.params['state']

    if module.check_mode:
        module.exit_json(changed=False)

    if state == 'present':
        changed, proxy_info = create_or_update_proxy(module, url, name, listen, upstream, enabled)
    else:  # state == 'absent'
        changed, proxy_info = delete_proxy(module, url, name)

    module.exit_json(changed=changed, proxy=proxy_info)

if __name__ == '__main__':
    main()
