Using IAM For Users
===================

.. note This document does not explain how Google Cloud IAM works, for that, please check out `the docs <https://cloud.google.com/iam/docs/>`_.

Resources that implement the IAM interface provide the following methods:

Policy Editing Methods
----------------------

>>> resource.add_roles(iam.user('alice@example.com'), resource.roles.OWNER, resource.roles.EDITOR)
True

The first argument is one of the IAM "Member" types:

- ``iam.user(email)`` an individual Google account
- ``iam.service_account(email)`` a Google Cloud Service Account
- ``iam.group(email)`` a Google group.
- ``iam.domain(domain_name)`` a Google-For-Work domain
- ``iam.ALL_AUTHENTICATED_USERS`` any authenticated user
- ``iam.ALL_USERS``

Note that all of these are convenience wrappers around strings. See the list of member string formats `here <https://cloud.google.com/iam/docs/managing-policies>`_.

All following arguments are roles to added to the specified member. Roles are simply strings that correspond to sets of permissions.
The resource should provide an enumeration of the possible "curated roles" for the resource.
You can acquire this list by running ``gcloud iam list-grantable-roles //fully/qualified/resource/path``.

This method returns ``True`` if the change to the resource's policy was made successfully, and returns ``False`` otherwise
(such as in the case of an update being made during this update).

>>> resource.remove_roles(iam.group('devs@example.com'), resource.roles.OWNER, resource.roles.EDITOR)
False

Same as above, but removes the specified roles from the specified member.

>>> resource.add_members(resource.roles.OWNER, iam.domain('example.com'), iam.service_account('compute@iam.my-project.example.com'))
True

Same as above, but the first argument is a role, and all subsequent arguments are members to which that role should be added.

>>> resource.remove_members(resource.roles.OWNER, iam.ALL_USERS)
True

Same as above, but removes all listed members from the specified role.

>>> def remove_fn(member):
>>>     return iam.is_group(member) or member == iam.user('bob@example.com')
>>> policy_change = iam.PolicyChange().add(resource.roles.OWNER, members=[iam.user('alice@example.com')])
>>>                                   .remove(resource.roles.EDITOR, members=[iam.group('devs@example.com']))
>>>                                   .remove(resource.roles.READER, fn=remove_fn)
>>> policy_change.apply(resource)
True

If you need more complex logic to modify an IAM policy you can create a ``iam.PolicyChange`` object.

``iam.PolicyChange`` exposes three methods. ``add`` and ``remove`` take a role, and a list of members, and add, or remove
those members from the specified roll respectively. ``remove`` also has the option of taking a ``fn`` keyword argument, which is a function object. This function takes a ``member`` string and returns whether or not the member should have the specified role. 

Finally, ``iam.PolicyChange`` exposes an ``apply`` method, which takes a resource, and applys the change to the resource.

Just like above, this method returns True if the change was successfully made, or False otherwise. 

>>> resource.set_policy({resource.roles.OWNER: [iam.user('alice@example.com')],
>>>                      resource.roles.EDITOR: [(iam.user('alice@example.com'), (iam.user('charles@example.com')]})

Finally, you can manually set the policy of a resource. Use this only if you don't need any transactionality guarantees.
If updates are made to your policy during this change, they will be overwritten with exactly what is in your policy.


Policy Access Methods
---------------------

As seen above, IAM Policies are simply dictionaries, of the following form. 

``{role_string: [member_string, member_string], role_string...}``

>>> resource.get_policy()
{'roles/owner': ['user:alice@example.com')], 'roles/editor': [('user:alice@example.com'), ('user:charles@example.com')]}

As you can see, when printed out roles and members will not be distinguishable from strings, (because they are strings).

>>> resource.get_roles(iam.user('alice@example.com'))
['roles/owner', 'roles/editor']

Takes a member, returns a list of roles which the member has.

>>> resource.get_members(resource.roles.OWNER)
['user:alice@example.com', 'group:devs@example.com']

Takes a role, and returns a list of the members who have that role.

Using IAM For Contributors
==========================

TODO(elibixby)
