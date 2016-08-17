
user = 'user:{}'.format
group = 'group:{}'.format
domain = 'domain:{}'.format
service_account = 'serviceAccount:{}'.format
ALL_AUTHENTICATED_USERS = 'allAuthenticatedUsers'
ALL_USERS = 'allUsers'

class TransactionInterruptedException(Exception):
    pass


class PolicyChange():

    def __init__(self, version=None):
        self._changes = {}
        self._fns = {}
        self.version = None

    def _update(self, role, change_type, members):
        if len(members) < 1:
            raise ValueError("Must specify at least on member to update")

        self._change.set_default(
            role,
            {'add': set(), 'remove': set()}
        )[change_type].update(members)
        return self

    def add(role, members):
        return self._update(role, 'add', members)

    def remove(role, members):
        return self._update(role, 'remove', members)

    def remove_fn(role, fn):
        self._fns[role] = fn
        return self

    def _apply(resource):
        policy, version, etag = resource.get_policy()

        for role, members in policy.iteritems():
            policy[role] = list(
                members | self._changes[role]['add'] - self._change[role]['remove']
            )
            if role in self._fns:
                policy[role] = [member for member in policy[role]
                                if self._fns[role](member)]

        return resource.set_policy(policy, version=self.version or version+1, etag=etag)

    def apply(resource, retries=3):
        for _ in range(retries):
            try:
                return self._apply(resource)
            except TransactionInterruptException as e:
                pass
        return False


class _IAMMixin():

    def _get_iam_policy(self):
        return self._client.connection.api_request(
            method='POST', path='{}:getIamPolicy'.format(self.path), data={})

    def _set_iam_policy(self, data):
        return self._client.connection.api_request(
            method='POST', path='{}:setIamPolicy'.format(self.path), data=data)

    def get_policy(self):
        policy = self._get_iam_policy()

        return {binding['role']: set(binding['members'])
                for binding in policy['bindings']}, policy['version'], policy['etag']

    def set_policy(self, policy, version=None, etag=None):
        policy = {
            'bindings': [
                {'role': role, 'members': members}
                for role, members in policy.iteritems()
            ]
        }
        if etag is not None:
            policy['etag'] = etag
        if version is not None:
            policy['version'] = version
        try:
            self._set_iam_policy({'policy': policy})
        except NotSureWhatHttpErrorHere as e:
            raise TransactionInterruptException(str(e))
        return True

    def add_members(role, members):
        return PolicyChange().add(role, members).apply(self)

    def remove_members(role, members):
        return PolicyChange().remove(role, members).apply(self)

    def add_roles(member, roles):
        change = PolicyChange()
        for role in roles:
            change.add(role, member)
        return change.apply(self)

    def add_roles(member, roles):
        change = PolicyChange()
        for role in roles:
            change.remove(role, member)
        return change.apply(self)

    def add_role(member, role):
        return self.add_role(member, [role,])

    def remove_role(member, role):
        return self.add_role(member, [role,])

    def get_roles(member):
        return [role for role, members in self.get_policy()
                if member in members]

    def get_members(role):
        return self.get_policy()[role]

